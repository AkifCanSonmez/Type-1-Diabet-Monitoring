import crud
from . import auth
import numpy as np
import io
from PIL import Image
import base64
import utils_common
from typing import List, Dict, Union
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Body, Form, UploadFile, status, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import sys
sys.path.append("..")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="",
    tags=["newmeal"],
    responses={404: {"description": "Todo not found"}}
)
templates = Jinja2Templates(directory="templates")


@router.post("/newmeal/detect-foods")
async def detect_foods(request: Request):
    user = await auth.get_current_user(request)
    image_data = await request.form()
    try:
        form = await request.form()
        file = form['uploaded_image'].file
        img = Image.open(file)
        # image.save("upload.jpg", "PNG")
    except:
        raise HTTPException(
            status_code=400, detail="No image found in the request.")

    detected_foods = utils_common.detect_foods(img, user_id=user["id"])
    request.session["detected_foods"] = detected_foods

    return RedirectResponse(url="/newmeal/nutritions", status_code=303)


@router.get("/newmeal/nutritions")
async def nutritions_page(request: Request, db: Session = Depends(get_db)):

    detected_foods = request.session.get("detected_foods")

    response = templates.TemplateResponse("detected_foods.html", {
                                          "request": request, "objects": detected_foods, "food_options": utils_common.food_options})
    return response


@router.post("/newmeal/nutritions")
async def add_meal_nutritions(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)
    form_data = await request.form()

    action = form_data.get("action")

    foods = form_data.getlist('foods')
    amounts = form_data.getlist('amounts')
    foods_n_amounts = dict(zip(foods, amounts))

    if action == "save_and_exit":

        # Adding foods and their amounts to database respect to current user
        crud.save_nutritions_and_exit(db, user, foods_n_amounts)

        return RedirectResponse(url="/logout", status_code=303)

    elif action == "continue":

        # For performance when user continue, adding nutritions information to session instead of db
        request.session["foods_n_amounts"] = foods_n_amounts

        return RedirectResponse(url="/newmeal/user-log/", status_code=303)


@router.get("/newmeal/user-log/")
async def user_log(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    bed_time = crud.get_bed_time_today(db, user["id"])

    extra_labels = []
    if bed_time is None:
        extra_labels = ["Bed Time", "Wake Up Time"]

    return templates.TemplateResponse("user_log.html", {"request": request, "extra_labels": extra_labels})


@router.post("/newmeal/add-todo")
async def record_newmeal(request: Request, db: Session = Depends(get_db)):
    # Control
    user = await auth.get_current_user(request)

    # getting user_log informations
    user_log = await request.form()

    # If this True, adding new meal done without save_and_exit
    if "foods_n_amounts" in request.session:

        # Get the meal foods and user log inputs from the request
        foods_n_amounts = request.session.get("foods_n_amounts")

        # adding new meal and deleting session objects
        crud.add_new_meal(db, user, foods_n_amounts, dict(user_log))

        # To avoid duplicating new data
        del request.session["foods_n_amounts"]

    else:
        # update user_log on new meal
        crud.update_new_meal_user_log(db, user, user_log)

    return RedirectResponse(url="/newmeal/similar-meals", status_code=303)


@router.get("/newmeal/similar-meals")
async def show_similar_meals(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    # getting similar meals, and ask user how insulin dose he will get (postprandial.html ile benzer bir html oluşturabilirsin)
    # Also last meal information retrieve to show user to compare
    similar_meals = crud.get_similar_meals(db, user["id"])
    print(similar_meals)
    new_meal = crud.get_last_meal_record(db, user["id"])

    return templates.TemplateResponse("similar_meals.html", {"request": request, "similar_meals": similar_meals,
                                                             "new_meal": new_meal})


@router.post("/newmeal/add-novorapid-dose")
async def update_novorapid_dose(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)
    form_data = await request.form()

    novorapid_dose = form_data["units"]
    crud.update_novorapid_dose(db, user["id"], novorapid_dose)
    return RedirectResponse(url="/home", status_code=303)

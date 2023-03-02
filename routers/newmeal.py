import sys
sys.path.append("..")

from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Body, Form, UploadFile, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List, Dict, Union
import cv2
import numpy as np
from . import auth
import crud

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

@router.get("/postprandial-sugar-control")
async def fullness_sugar_control(request: Request, db:Session=Depends(get_db)):

    # Get the user from the session
    user = await auth.get_current_user(request)

    last_meals = crud.check_fullness_last_3_meals(db, user["id"])
    if last_meals:
        # If there are meals without fullness sugar entered, render a template
        # that includes the details of those meals and a form to allow the user
        # to enter the fullness sugar
        return templates.TemplateResponse(
            "fullness_sugar.html",
            {"request": request, "last_meals": last_meals},
        )
    else:
        # If all meals have fullness sugar entered, redirect the user to the
        # home page
        return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
            

@router.get("/home/newmeal")
async def newmeal_page(request: Request):
    return templates.TemplateResponse("newmeal.html", {"request": request})


@router.post("/meal/nutritions/")
async def meal_info(request: Request):
    form_data = await request.form()
    form_name = form_data.get("form_name")

    if form_name == "typing":
        response = templates.TemplateResponse("foods.html", {"request": request})
    elif form_name == "send_image":
        food_image = form_data.get("food_image").file
        #image = cv2.imdecode(np.frombuffer(food_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        detected_foods = ["bulgur","apple","chicken"]
        response = templates.TemplateResponse("foods.html", {"request": request, "objects": detected_foods})
    return response


#This api will use /meal/typing-nutritions and /meal/nutritions to add inputs to session
@router.post("/temporary-storage-for-inputs")
async def temporary_storage(request: Request, db:Session=Depends(get_db)):
    payload = await request.json()
    request.session["foods_amounts"] = payload
    user = await auth.get_current_user(request)

    #wake up time and bet time bars added session
    bed_time = crud.get_bed_time_today(db,user["id"])
    
    if bed_time is None:
        request.session["extra_labels"] = ["Bed Time", "Wake Up Time"]

    return {"Status": "Redirecting to /meal/user-log in foods.js code"}

@router.get("/meal/user-log/")
async def user_log(request: Request):
    extra_labels = request.session.get("extra_labels", []) # use get method to safely retrieve the data
    return templates.TemplateResponse("user_log.html", {"request": request, "extra_labels": extra_labels})

#add_meal olacak
@router.post("/newmeal/add-todo")
async def record_newmeal(request: Request, db:Session=Depends(get_db)):

    #Control
    user = await auth.get_current_user(request)
    if user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Get the meal foods and user log inputs from the request
    meal_foods_amounts = request.session.get("foods_amounts")
    user_log = await request.form()
  
    print(crud.add_new_meal(db,user, meal_foods_amounts, user_log))
    return RedirectResponse(url="/newmeal/similar-meals", status_code=status.HTTP_302_FOUND)
    #Redirect Response to similar_meals

#Will be Updated
@router.get("/newmeal/similar-meals")
async def show_similar_meals(request: Request, db:Session=Depends(get_db)):
    user = await auth.get_current_user(request)
    #request session clear eklemeyi unutma
    query = crud.check_fullness_last_3_meals(db,user["id"] )
    for q in query:
        print(q.fullness_sugar)
    return "Finish"



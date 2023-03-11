import sys
sys.path.append("..")

from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Body, Form, UploadFile, status, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List, Dict, Union
import algorithms_
import base64
from PIL import Image
import io
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

    
@router.post("/add-postprandial-glucose-last-meal")
async def add_postprandial_glucose_last_meal(request: Request, db:Session=Depends(get_db)):
    user = await auth.get_current_user(request)
    form_data = await request.form()
    postprandial_glucose  = form_data.get("postprandial_glucose")
    postprandial_glucose = crud.update_postprandial_glucose_row(db, user["id"], postprandial_glucose)
    print(postprandial_glucose)
    return RedirectResponse("/home/", status_code=status.HTTP_302_FOUND)
 

@router.post("/meal/nutritions/")
async def meal_info(request: Request):
    image_data = await request.form()
    user = await auth.get_current_user(request)
    try:
        form = await request.form()
        file = form['uploaded_image'].file
        img = Image.open(file)
        #image.save("upload.jpg", "PNG")
    except:
        raise HTTPException(status_code=400, detail="No image found in the request.")
    
    detected_foods = algorithms_.detect_foods(img, user_id=user["id"])
    response = templates.TemplateResponse("detected_foods.html", {"request": request, "objects": detected_foods})
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

    #getting similar meals, and ask user how insulin dose he will get (postprandial.html ile benzer bir html oluşturabilirsin)
    #algorithms_.get_similar_meals(db, user["id"])
    return templates.TemplateResponse("similar_meals.html", {"request": request})
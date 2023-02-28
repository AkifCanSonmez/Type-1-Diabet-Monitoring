import sys
sys.path.append("..")

from fastapi import APIRouter, Request, Body, Form, UploadFile, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List, Dict, Union
from sqlalchemy.orm import Session
from database import SessionLocal
import cv2
import numpy as np
import crud

router = APIRouter(
    prefix="",
    tags=["todos"],
    responses={404: {"description": "Todo not found"}}
)
templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


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
async def temporary_storage(request: Request):
    payload = await request.json()
    request.session["foods"] = payload
    return {"Status": "Session'a eklendi"}

@router.get("/meal/user-log/")
async def user_log(request: Request):
    return templates.TemplateResponse("user_log.html", {"request": request})

@router.post("/control")
async def control(request: Request, db:Session=Depends(get_db)):
    meal_foods = request.session.get("foods")
    form_data = await request.form()
    user_log = dict(form_data)
    crud.add_meal(db, meal_foods, user_log)
    return "Tamamlandı"
    #artık db işlemleri başlayacak


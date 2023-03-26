from . import auth
import crud
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, Depends, status
import sys
sys.path.append("..")


templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="",
    tags=["home"],
    responses={401: {"user": "Not authorized"}}
)


@router.get("/home")
async def home(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    missing_new_meal = crud.get_missing_new_meal(db, user["id"])

    if missing_new_meal is not None:
        case = "continue_new_meal"
    else:
        missing_novorapid_dose = crud.get_missing_novorapid_dose(
            db, user["id"])
        missing_postprandial_glucose = crud.get_missing_postprandial_glucose(
            db, user["id"])

        if missing_novorapid_dose is not None:
            case = "add_novorapid_dose"

        elif missing_postprandial_glucose is not None:
            case = "add_postprandial_glucose"

        else:
            case = "default"

    return templates.TemplateResponse("home.html", {
        "request": request,
        "case": case
    })


@router.post("/add-postprandial-glucose-last-meal")
async def add_postprandial_glucose_last_meal(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    form_data = await request.form()
    postprandial_glucose = form_data.get("postprandial_glucose")
    crud.update_postprandial_glucose_row(db, user["id"], postprandial_glucose)
    return RedirectResponse("/home/", status_code=status.HTTP_302_FOUND)


@router.get("/continue-new-meal")
async def continue_new_meal(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    missing_new_meal = crud.get_missing_new_meal(db, user["id"])
    return templates.TemplateResponse("missing_new_meal.html", {"request": request,
                                                                "missing_new_meal": missing_new_meal})


@router.get("/missing-postprandial-glucose")
async def missing_postprandial_glucose(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    missing_postprandial_glucose = crud.get_missing_postprandial_glucose(
        db, user["id"])
    return templates.TemplateResponse("postprandial_enter.html", {"request": request,
                                                                  "data": missing_postprandial_glucose})

# If user doesn't continue to adding new meal, missing data will removed from db


@router.post("/delete-missing-and-redirect")
async def deneme(request: Request, db: Session = Depends(get_db)):
    user = await auth.get_current_user(request)

    crud.delete_missing_data(db, user["id"])
    return RedirectResponse(url="/home", status_code=303)

import crud
from . import auth
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, status, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import sys
sys.path.append("..")


router = APIRouter(
    prefix="",
    tags=["meal_suggestions"],
    responses={401: {"user": "Not authorized"}}
)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/home/meal-suggestions")
async def meal_suggestions(request: Request, db: Session = Depends(get_db)):
    fasting_glucose = int(request.query_params.get('fasting-glucose'))
    meal_time = request.query_params.get('meal-time')
    activity_status = request.query_params.get('did-activity')
    user = await auth.get_current_user(request)
    print(activity_status, type(activity_status))
    # Getting 6 meals, 3 meals where postprandial glucose is good, and others bad high glucose
    (data_w_good_glucose, data_w_high_glucose) = crud.get_meal_suggestions(
        db=db,
        fasting_glucose=fasting_glucose,
        meal_time=meal_time,
        activity_status=activity_status,
        user_id=user["id"],
    )

    return templates.TemplateResponse("meal_suggestions.html", {"request": request,
                                                                "data_w_good_glucose": data_w_good_glucose,
                                                                "data_w_high_glucose": data_w_high_glucose})

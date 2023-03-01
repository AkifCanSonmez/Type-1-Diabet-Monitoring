import sys
sys.path.append("..")

from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
from algorithms_ import convert_str_to_float
from database import SessionLocal
#from algorithms_ import similar_meal_algorithm
from fastapi import APIRouter, Request, Body, Form, UploadFile, status, Depends

router = APIRouter(
    prefix="",
    tags=["crud"],
    responses={404: {"description": "Todo not found"}}
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# CRUD Operations for NewMeal Page
#-----------------------------------------------------------------------------------
# Query if last meal's fasting sugar and insulin dose added
def query_last_meal(db:Session):
    pass

# Get Similar Meals
def get_similar_meals(db:Session):
    #similar_meal_algorithm()
    pass

#From NutritionDB getting inputs foods nutritional information
def get_nutritional_informations(db:Session, foods:list):
    #Getting food nutrition values from DB
    query_nutrition_values = db.query(models.NutritionDB).filter(or_(*[models.NutritionDB.food_name == food for food in foods])).all()
    return query_nutrition_values

#processing inputs for meal_nutritions
def process_nutrition_inputs(db: Session, foods_amounts: dict):
    query_nutrition_values = get_nutritional_informations(db, foods_amounts.keys() )

    #Class Object to be returned
    class columns_nutritions:
        def __init__(self):
            self.carbohydrate_sources: str = ""
            self.carbohydrate_amount_total: float = 0.0
            self.protein_amount_total: float = 0.0
            self.fat_amount_total: float = 0.0
            self.calories_amount_total: float = 0.0
            self.carbohydrate_source_main: str = ""
            self.carbohydrate_amount_main: float = 0.0
            self.gi_score_of_main_carb: int = 0
    cols = columns_nutritions()
    
    #Used for detecting carb sources, max carb source(main_carb) & gi of main carb
    foods_carb_values: dict = {}

    #Calculating     
    for query in query_nutrition_values:
        food = query.food_name
        food_amount = float(foods_amounts[food])
        
        #Getting Foods' carb-protein-fat nutritions values in 100g
        #nutrition values stored in str like '60(g)', '17(g)' etc.
        carb_100, protein_100, fat_100 = convert_str_to_float(query.carbohydrate_100g, query.protein_100g, query.fat_100g)

        #Calculating nutrition values for meal food
        cols.carbohydrate_amount_total += carb_100 * (food_amount/100)
        cols.protein_amount_total += protein_100 * (food_amount/100)
        cols.fat_amount_total += fat_100 * (food_amount/100)
        cols.calories_amount_total += float(query.calories_100g) * (food_amount/100)
        foods_carb_values[food] = carb_100 * (food_amount/100)
    
    for food in foods_carb_values:
        food_carb_value = foods_carb_values[food]
        total_carb_value = cols.carbohydrate_amount_total 

        percentage = 0.2
        if food_carb_value >= total_carb_value * percentage:
            cols.carbohydrate_sources += f", {food}"

    #Main carbohydrate will be food with max carbs amount
    cols.carbohydrate_source_main = max(foods_carb_values)
    cols.carbohydrate_amount_main = foods_carb_values[cols.carbohydrate_source_main]

    #gi_score will be main carb's gi score
    cols.gi_score_of_main_carb = db.query(models.NutritionDB.glycemic_index).filter(models.NutritionDB.food_name==cols.carbohydrate_source_main).first()
    
    return cols



#add_meal olacak
@router.post("/newmeal/add-todo/meal-nutrition")
async def add_todo_meal_nutrition(request: Request, db:Session=Depends(get_db)):
    meal_foods = request.session.get("foods")
    form_data = await request.form()
    user_log = dict(form_data)

    foods_amounts = dict(zip(meal_foods["foods"],meal_foods['amounts'] ))

    #todo_model for meal_nutritions
    todo_model = models.MealNutrition()

    #calculate meal foods nutrition values
    cols = process_nutrition_inputs(db, foods_amounts)
    for key, value in vars(cols).items():
        print(f"{key}: {value}")
    #add foods to meal_nutritions (return pk)
    
    #add user-log to user_log (return pk)

    #add meal_info (return pk)

    #last_id = db.query(models.FoodNutrition).order_by(models.FoodNutrition.pk_food.desc()).first()
    return "Calıstı"











#-----------------------------------------------------------------------------

# CRUD Operations for Analysis Page
#--------------------------------------------------------------------------------
#lantus için gerekebilir
def get_fasting_blood_sugars(db:Session, number: int = 10):
    pass

def get_average_information(db:Session):
    #1aylık verileri çek
    #algorithm.py'den hba1c, günlük ort carb,yağ,protein algoritmasını yaparsın 
    pass

def get_fullness_blood_sugars(db:Session, number: int = 10):
    pass

def get_critic_fulness_sugar_meal(db:Session, number: int = 10):
    pass

def get_daily_calories(db:Session, number: int = 10):
    pass


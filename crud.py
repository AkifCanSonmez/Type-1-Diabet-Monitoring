import sys
sys.path.append("..")

from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
from algorithms_ import convert_str_to_float
#from algorithms_ import similar_meal_algorithm

# CRUD Operations for NewMeal Page
#-----------------------------------------------------------------------------------
# Query if last meal's fasting sugar and insulin dose added
def query_last_meal(db:Session):
    pass

# Get Similar Meals
def get_similar_meals(db:Session):
    #similar_meal_algorithm()
    pass

#def get_food_nutritions(db, meal_nutritions)

#def calculate_nutritions()

def get_food_nutritions(db:Session, foods:list):
    #Getting food nutrition values from DB
    query_nutrition_values = db.query(models.NutritionDB).filter(or_(*[models.NutritionDB.food_name == food for food in foods])).all()
    return query_nutrition_values


def calculate_nutrition_values(db: Session, foods_amounts: dict):
    query_nutrition_values = get_food_nutritions(db, foods_amounts.keys() )

    #Columns for meal_nutrition DB
    carbohydrate_sources: str
    carbohydrate_amount_total: float = 0.0
    protein_amount_total: float = 0.0
    fat_amount_total: float = 0.0
    calories_amount_total: float
    carbohydrate_source_main: str
    carbohydrate_amount_main: float

    #This will be used for detecting max carb source
    carb_sources_and_amounts: dict = {}

    #Calculating     
    for query in query_nutrition_values:
        food = query.food_name
        food_amount = float(foods_amounts[food])
        
        #Getting Foods' carb-protein-fat nutritions values in 100g
        #nutrition values stored in str like '60(g)', '17(g)' etc.
        carb_100, protein_100, fat_100 = convert_str_to_float(query.carbohydrate_100g, query.protein_100g, query.fat_100g)
        
        #Calculating nutrition values for meal food
        carb_sources_and_amounts[food] = carb_100 * (food_amount/100)
        protein_amount_total += protein_100 * (food_amount/100)
        fat_amount_total += fat_100 * (food_amount/100)
    print("Result:",carb_sources_and_amounts,protein_amount_total, fat_amount_total )


# Add new Meals
def add_meal(db:Session, meal_foods, user_log):
    #Dict for Foods and Their Amounts
    foods_amounts = dict(zip(meal_foods["foods"],meal_foods['amounts'] ))

    #todo_model for meal_nutritions
    todo_model = models.MealNutrition()

    #calculate meal foods nutrition values
    calculate_nutrition_values(db, foods_amounts)
    #last_id = db.query(models.FoodNutrition).order_by(models.FoodNutrition.pk_food.desc()).first()
    return













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


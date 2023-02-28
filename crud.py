from sqlalchemy.orm import Session
import models
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

# Add new Meals
def add_meal(db:Session):
    pass
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


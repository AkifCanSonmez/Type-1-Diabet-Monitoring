import sys
sys.path.append("..")

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
import tables
import decimal
import datetime
from algorithms_ import convert_str_to_float
from database import SessionLocal
from datetime import timedelta
#from algorithms_ import similar_meal_algorithm


# CRUD Operations for NewMeal Page
#-----------------------------------------------------------------------------------
# Query if last meal's fasting glucose and insulin dose added
#From NutritionDB getting inputs foods nutritional information
def get_mealRecord_for_glucoseAnalysis(db:Session, user_id:int, day: int):

    query = db.query(tables.UserLog.fasting_glucose,
                    tables.MealNutrition.carbohydrate_amount_total,
                    tables.UserLog.novorapid_dose,
                    tables.MealNutrition.carbohydrate_sources,
                    tables.UserLog.did_activity,
                    tables.UserLog.minutes_after_activity,
                    tables.MealRecord.fk_user,
                    tables.UserLog.meal_time,
                    tables.MealRecord.record_id)\
            .filter(tables.MealRecord.fk_user == user_id, tables.UserLog.meal_time >= datetime.datetime.now() - timedelta(days=day))\
            .join(tables.MealRecord, tables.MealRecord.fk_user_log == tables.UserLog.pk_user_log)\
            .join(tables.MealNutrition, tables.MealRecord.fk_meal_nutritions == tables.MealNutrition.pk_meal_nutrition)\
            .order_by(tables.UserLog.meal_time.desc())\
            .limit(10)\
            .all()
    return query

#def get_mealRecord_for_nutritionAnalysis(db:Session, user_id:int, day:int):

def get_avg_nutritions(db:Session, user_id:int):
    two_months_ago = datetime.datetime.now() - datetime.timedelta(days=60)
    query = db.query(
            func.date_trunc('month', tables.UserLog.meal_time).label("month"),
            func.avg(tables.MealNutrition.calories_amount_total).label("avg_calories"),
            func.avg(tables.MealNutrition.carbohydrate_amount_main).label("avg_carbs"),
            func.avg(tables.MealNutrition.protein_amount_total).label("avg_protein"),
            func.avg(tables.MealNutrition.fat_amount_total).label("avg_fat")
        ) \
        .join(tables.MealRecord, tables.MealRecord.fk_user_log == tables.UserLog.pk_user_log) \
        .filter(tables.MealNutrition.pk_meal_nutrition == tables.MealRecord.fk_meal_nutritions,
                tables.MealRecord.fk_user == user_id,
                tables.UserLog.meal_time >= two_months_ago) \
        .group_by("month") \
        .all()

    return query
    


def get_nutritional_informations(db:Session, foods:list):
    #Getting food nutrition values from DB
    query_nutrition_values = db.query(tables.NutritionDB).filter(or_(*[tables.NutritionDB.food_name == food for food in foods])).all()
    return query_nutrition_values

#Send to temporary storage
def get_bed_time_today(db:Session, current_user_id: int):
    
    #innerjoin- lefjoin vs.bunları araştır ona göre yap
    last_row = db.query(tables.UserLog).join(tables.MealRecord).\
                filter(tables.MealRecord.fk_user == current_user_id).\
                order_by(tables.UserLog.pk_user_log.desc()).first()
    
    return last_row.bed_time
    
    try:
        if last_row is None or last_row.bed_time is None or last_row.bed_time.date() != datetime.date.today():
            return None
        else:
            return "There is already bed time for today"
    except:
        print("ERROR")

def check_postprandial_glucose_last_meal(db:Session, user_id:int):
    #try ekle eğer tabloda bir şey yokken hata verirse
    latest_meal_record = db.query(tables.MealRecord)\
                            .filter(tables.MealRecord.fk_user == user_id)\
                            .order_by(tables.MealRecord.record_id.desc())\
                            .first()
    if latest_meal_record.user_log.postprandial_glucose == None:
        return latest_meal_record
    else:
        return None

def update_postprandial_glucose_row(db:Session, user_id, postprandial_glucose):
    latest_meal_record = db.query(tables.MealRecord)\
                            .filter(tables.MealRecord.fk_user == user_id)\
                            .order_by(tables.MealRecord.record_id.desc())\
                            .first()
    latest_meal_record.user_log.postprandial_glucose = postprandial_glucose
    db.commit()

    return "Completed"

# Get Similar Meals
def get_similar_meals(db:Session):
    #similar_meal_algorithm()
    pass


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
    carbs_of_foods: dict = {}

    #Calculating     
    for query in query_nutrition_values:
        food = query.food_name
        food_amount = float(foods_amounts[food])
        
        #Getting Foods' carb-protein-fat nutritions values in 100g
        #nutrition values stored in str like '60(g)', '17(g)' etc.
        carb_100, protein_100, fat_100 = convert_str_to_float(query.carbohydrate_100g, query.protein_100g, query.fat_100g)

        #Calculating nutrition values for meal food
        food_carb_amount = carb_100 * (food_amount/100)
        cols.carbohydrate_amount_total += food_carb_amount
        cols.protein_amount_total += protein_100 * (food_amount/100)
        cols.fat_amount_total += fat_100 * (food_amount/100)
        cols.calories_amount_total += float(query.calories_100g) * (food_amount/100)
        carbs_of_foods[food] = carb_100 * (food_amount/100)

        #Main carbohydrate will be food with max carbs amount
        if food_carb_amount > cols.carbohydrate_amount_main:
            cols.carbohydrate_amount_main = food_carb_amount
            cols.carbohydrate_source_main = food
    
    #Total carb'in %25'ine eşit olan carblar ekleniyor
    carbs_source_list = []
    percentage = 0.25
    for food in carbs_of_foods:
        food_carb_value = carbs_of_foods[food]
        total_carb_value = cols.carbohydrate_amount_total 
        if food_carb_value >= total_carb_value * percentage:
            carbs_source_list.append(food)
    cols.carbohydrate_sources = ",".join(carbs_source_list)



    #gi_score will be main carb's gi score
    cols.gi_score_of_main_carb = db.query(tables.NutritionDB.glycemic_index).filter(tables.NutritionDB.food_name==cols.carbohydrate_source_main).first()[0]
    
    return cols

def process_user_log_inputs(db:Session, user_log):
    
    #Will be Returned
    class user_log_columns:
        def __init__(self):
            self.fasting_glucose: int
            self.postprandial_glucose: int
            self.novorapid_dose: int
            self.hunger_status: str
            self.did_activity: bool
            self.minutes_after_activity: int
            self.meal_time: str
            self.bed_time: str
            self.wake_up_time: str
    col = user_log_columns()

    col.did_activity = True if user_log['did-activity'] else False
    col.hunger_status = user_log['hunger-status']
    col.fasting_glucose = user_log['fasting-glucose']

    act_end = datetime.datetime.strptime(user_log["activity-end-time"], "%H:%M").time() # convert to datetime object
    now = datetime.datetime.now().replace(second=0, microsecond=0).time() # get current time and remove seconds/microseconds  
    col.minutes_after_activity = ((now.hour - act_end.hour) * 60) + now.minute - act_end.minute 
    col.meal_time = datetime.datetime.now()
    try:
        if user_log["Bed Time"]:
            bed_time = datetime.datetime.strptime(user_log["Bed Time"], "%H:%M").time()
            wake_up_time = datetime.datetime.strptime(user_log["Wake Up Time"], "%H:%M").time()
            now = datetime.datetime.now()
            
            #Getting TIMESTAMP value
            col.bed_time = result = datetime.datetime.combine(now.date(), bed_time)
            col.wake_up_time = datetime.datetime.combine(now.date(), wake_up_time)
    except:
        #If there is bed&wake up time for same day in db, use this for new row
        last_row = db.query(tables.UserLog).order_by(tables.UserLog.pk_user_log.desc()).first()
        col.bed_time = last_row.bed_time
        col.wake_up_time = last_row.wake_up_time
    
    return col
    
        #benzer yemeklerden sonra dönüp update edersin update altında
        #todo_model.novorapid_dose = None

        #son girişte sorup update edersin update altında
        #todo_model.postprandial_glucose
    

def add_todo_meal_nutrition(db:Session, meal_foods_amounts):

    # Create a dictionary of foods and their amounts from the meal_foods dictionary
    # This will be passed to the process_nutrition_inputs function to calculate the nutrition values
    foods_amounts = dict(zip(meal_foods_amounts["foods"], meal_foods_amounts['amounts']))

    # Create a new MealNutrition object and populate it with the nutrition values calculated from the inputs
    todo_model = tables.MealNutrition()

    # Calculate the nutrition values for the meal and populate the todo_model object
    cols = process_nutrition_inputs(db, foods_amounts)

    todo_model.carbohydrate_amount_total = decimal.Decimal(str(cols.carbohydrate_amount_total)).quantize(decimal.Decimal('.1'))
    todo_model.carbohydrate_amount_main = decimal.Decimal(str(cols.carbohydrate_amount_main)).quantize(decimal.Decimal('.1'))
    todo_model.calories_amount_total = decimal.Decimal(str(cols.calories_amount_total)).quantize(decimal.Decimal('.1'))
    todo_model.carbohydrate_source_main = cols.carbohydrate_source_main
    todo_model.carbohydrate_sources = cols.carbohydrate_sources
    todo_model.fat_amount_total = decimal.Decimal(str(cols.fat_amount_total)).quantize(decimal.Decimal('.1'))
    todo_model.gi_score_of_main_carb = cols.gi_score_of_main_carb
    todo_model.protein_amount_total = decimal.Decimal(str(cols.protein_amount_total)).quantize(decimal.Decimal('.1'))


    # Add the meal nutrition objects to the meal_nutrition table and return its PK
    db.add(todo_model)
    db.commit()
    return todo_model.pk_meal_nutrition

def add_todo_user_log(db:Session, user_log):
    todo_model = tables.UserLog()
    cols = process_user_log_inputs(db,user_log)

    todo_model.bed_time = cols.bed_time
    todo_model.did_activity = cols.did_activity
    todo_model.fasting_glucose = cols.fasting_glucose
    todo_model.hunger_status = cols.hunger_status
    todo_model.meal_time = cols.meal_time
    todo_model.minutes_after_activity = cols.minutes_after_activity
    todo_model.wake_up_time = cols.wake_up_time
    
    db.add(todo_model)
    db.commit()
    return todo_model.pk_user_log

def add_new_meal(db:Session, user, meal_foods_amounts, user_log):
    user_log = dict(user_log)
    print(user_log)
    pk_user = user["id"]
    pk_meal_nutrition = add_todo_meal_nutrition(db, meal_foods_amounts)
    pk_user_log = add_todo_user_log(db, user_log)
    
    todo_model = tables.MealRecord()
    todo_model.fk_meal_nutritions = pk_meal_nutrition
    todo_model.fk_user = pk_user
    todo_model.fk_user_log = pk_user_log
    db.add(todo_model)
    db.commit()
    return {"KEYS": {"PK_MealNutrition": pk_meal_nutrition, "PK_UserLog": pk_user_log, "PK_User": pk_user,
            "FK_MealNutrition": todo_model.fk_meal_nutritions, "FK_UserLog": todo_model.fk_user_log, "FK_User": todo_model.fk_user}}














#-----------------------------------------------------------------------------

# CRUD Operations for Analysis Page
#--------------------------------------------------------------------------------
#lantus için gerekebilir
def get_fasting_glucose(db:Session, number: int = 10):
    pass

def get_average_information(db:Session):
    #1aylık verileri çek
    #algorithm.py'den hba1c, günlük ort carb,yağ,protein algoritmasını yaparsın 
    pass

def get_postprandial_glucose(db:Session, number: int = 10):
    pass

def get_critic_postprandial_glucose_meal(db:Session, number: int = 10):
    pass

def get_daily_calories(db:Session, number: int = 10):
    pass










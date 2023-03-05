import sys
sys.path.append("..")
from sqlalchemy.orm import Session, contains_eager
import tables
import os
import torch

model = torch.hub.load('ultralytics/yolov5', 'custom', path='last.pt', force_reload=False)


def convert_str_to_float(*params):
    converted_values = []
    for text in params:
        converted_text = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
        converted_values.append(converted_text)
    return tuple(converted_values)

def get_similar_meals(db:Session, user_id):
    new_meal = db.query(tables.MealRecord).\
    filter(tables.MealRecord.fk_user == user_id).\
    order_by(tables.MealRecord.record_id.desc()).first()

    meal_records = db.query(tables.MealRecord).\
        join(tables.MealRecord.nutritions).\
        options(
            contains_eager(tables.MealRecord.nutritions).load_only(tables.MealNutrition.carbohydrate_sources, tables.MealNutrition.carbohydrate_amount_total,
                                                                tables.MealNutrition.carbohydrate_source_main, tables.MealNutrition.carbohydrate_amount_main,
                                                                tables.MealNutrition.gi_score_of_main_carb),
            contains_eager(tables.MealRecord.user_log).load_only(tables.UserLog.fasting_glucose, tables.UserLog.postprandial_glucose, tables.UserLog.novorapid_dose,
                                                                tables.UserLog.did_activity, tables.UserLog.minutes_after_activity, tables.UserLog.meal_time)
        ).\
        filter(tables.MealRecord.fk_user == user_id, tables.UserLog.did_activity == new_meal.user_log.did_activity, 
            tables.MealRecord.record_id != new_meal.record_id)
    

    if len(meal_records.all()) > 0:
        similar_meals = []
        #Carb Sources'e göre parçalandı
        data_1 = meal_records.filter(tables.MealNutrition.carbohydrate_sources == new_meal.nutritions.carbohydrate_sources)
        data_2 = meal_records.filter(tables.MealNutrition.carbohydrate_sources != new_meal.nutritions.carbohydrate_sources)
        
        control = True
        # Carb Source Main'e göre parçalandı
        for data in list(data_1, data_2):
            sub_data_1 = data.filter(tables.MealNutrition.carbohydrate_source_main == new_meal.nutritions.carbohydrate_source_main)
            sub_data_2 = data.filter(tables.MealNutrition.carbohydrate_source_main != new_meal.nutritions.carbohydrate_source_main)
        
            # Carb amount total'e göre parçalandı
            for data in list(sub_data_1, sub_data_2):
                sub_sub_data_1 = data.filter(tables.MealNutrition.carbohydrate_amount_total == new_meal.nutritions.carbohydrate_amount_total)
                sub_sub_data_2 = data.filter(tables.MealNutrition.carbohydrate_amount_total != new_meal.nutritions.carbohydrate_amount_total)

                # Fasting glukose göre parçalandı
                for data in list(sub_sub_data_1, sub_sub_data_2):
                    sub_sub_sub_data_1 = data.filter(tables.UserLog.fasting_glucose == new_meal.user_log.fasting_glucose)
                    sub_sub_sub_data_2 = data.filter(tables.UserLog.fasting_glucose != new_meal.user_log.fasting_glucose)

                    #Order By Postprandial
                    for data in list(sub_sub_sub_data_1, sub_sub_sub_data_2):
                        data.order_by(tables.UserLog.postprandial_glucose)
                        if len(data.all()) > 0:
                            similar_meals.append(data.all())

                            if len(similar_meals) >= 3:
                                break
                        if not control:
                            break
                    if not control:
                        break
                if not control:
                    break
            if not control:
                break
    

def detect_foods(img, user_id):
    #img.save(f"upload_{user_id}.png", "PNG")
    results = model(img, size=640) # batch of images
    detected_foods = list(set(results.pandas().xyxy[0]["name"]))
    return detected_foods
    #os.remove(f"upload_{user_id}.png")
    
               









        

        #print(len(meal_records))
        #split meal_records
        #"CODE ..."
        
        #if meal_records is not None:
        
    




def calculate_minimum_nutrition_requirements(query):
    """
    Calculates minimum calorie, protein, fat, and carbohydrate requirements.
    Uses the Mifflin St. Jeor equation to calculate Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE)
    based on activity level. Returns results in a dictionary.

    :param gender: str, "male" or "female"
    :param age: int, age in years
    :param height_cm: int, height in centimeters
    :param weight_kg: float, weight in kilograms
    :param activity_level: str, one of "sedentary", "lightly active", "moderately active", "very active", "extra active"
    :param diabetes_type: str, "type1" or "type2"

    :return: dict, minimum calorie, protein, fat, and carbohydrate requirements
    """
    gender = query.gender
    age = query.age
    height_cm = query.height
    weight_kg = query.weight
    activity_level = query.activity_level

    # Define activity level multipliers for TDEE calculation
    activity_levels = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9
    }

    # Calculate BMR using Mifflin St. Jeor equation
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Calculate TDEE based on physical activity level
    tdee = bmr * activity_level
    
    # Calculate minimum calorie requirement based on diabetes type 1
    min_calories = tdee * 0.8

    # Calculate minimum protein requirement (1.2 g/kg of body weight)
    min_protein = 1.2 * weight_kg

    # Calculate minimum fat requirement (20-35% of total calorie intake)
    min_fat_calories = min_calories * 0.2
    max_fat_calories = min_calories * 0.35
    min_fat = min_fat_calories / 9  # 1 gram of fat has 9 calories

    # Calculate minimum carbohydrate requirement (remaining calories after protein and fat requirements are met)
    remaining_calories = min_calories - (min_protein * 4 + min_fat * 9)
    min_carbs = remaining_calories / 4  # 1 gram of carbohydrate has 4 calories

    # Return dictionary of minimum requirements
    return {"calories": int(min_calories), "protein": int(min_protein), "fat": int(min_fat), "carbs": int(min_carbs)}



''' 
def hba1c():
    HbA1c (%) = (average blood glucose level in mg/dL + 46.7) / 28.7
    HbA1c (%) = (126.7 + 46.7) / 28.7
    HbA1c (%) = 5.9%
    pass

  '''
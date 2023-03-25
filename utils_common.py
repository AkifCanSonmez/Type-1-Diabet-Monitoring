import torch
import os
from tables import MealNutrition, Account, MealRecord, UserLog, NutritionDB

import sys
sys.path.append("..")

model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='last.pt', force_reload=False)


# food_options is a list of foods whose information is in the nutrition database
file = open("../predefined_classes.txt").readlines()
food_options = [x.rstrip() for x in file]
food_options.sort()

# To processing some str values in db (Nutrition values are stored in str type like '60(g)', '17(g)' etc.)
def convert_str_to_float(*params):
    converted_values = []
    for text in params:
        converted_text = float(
            ''.join(filter(lambda x: x.isdigit() or x == '.', text)))
        converted_values.append(converted_text)
    return tuple(converted_values)

# yolov5 food detect operation
def detect_foods(img, user_id):
    results = model(img, size=640)  # batch of images
    detected_foods = list(set(results.pandas().xyxy[0]["name"]))
    return detected_foods


def calculate_hba1c(query):
    # Calculating estimated HbA1C based on A1C-Derived Average Glucose Formula
    # The Result of this isn't CERTAIN!!

    hba1c_list = []
    for month_data in query:
        avg_fasting_glucose = month_data.avg_fasting_glucose
        avg_postprandial_glucose = month_data.avg_postprandial_glucose
        #!!!!avg_bedtime_glucose = month_data.avg_bedtime_glucose

        # Calculate average blood glucose level in mg/dL

        #!!!!avg_blood_glucose = (avg_fasting_glucose * 0.5) + (avg_postprandial_glucose * 0.3) + (avg_bedtime_glucose * 0.2)
        avg_blood_glucose = (int(avg_fasting_glucose) * 0.5) + \
            (int(avg_postprandial_glucose) * 0.5)

        # Calculate HbA1c percentage
        hba1c = (avg_blood_glucose + 46.7) / 28.7

        # Round to one decimal place
        hba1c = round(hba1c, 1)

        hba1c_list.append((month_data.month, hba1c))

    return hba1c_list


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


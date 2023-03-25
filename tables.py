from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base


class Account(Base):
    __tablename__ = 'account'
    pk_user = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    user_password = Column(String(30))
    email = Column(String(70), unique=True)
    age = Column(Integer)
    weight = Column(Numeric(4, 1))
    height = Column(Numeric(4, 1))
    body_fat = Column(Numeric(3, 1))
    activity = Column(String(20))
    created_on = Column(TIMESTAMP)


class NutritionDB(Base):
    __tablename__ = 'nutritions_db'
    pk_food = Column(Integer, primary_key=True)
    food_name = Column(String)
    carbohydrate_100g = Column(String)
    protein_100g = Column(String)
    fat_100g = Column(String)
    fiber_100g = Column(String)
    cholesterol_100g = Column(String)
    sodium_100g = Column(String)
    potassium_100g = Column(String)
    calcium_100g = Column(String)
    vitamin_a_100g = Column(String)
    vitamin_c_100g = Column(String)
    iron_100g = Column(String)
    calories_100g = Column(Numeric(6, 1))
    glycemic_index = Column(Integer)

class MealNutrition(Base):
    __tablename__ = 'meal_nutrition'
    pk_meal_nutrition = Column(Integer, primary_key=True)
    carbohydrate_sources = Column(String)
    carbohydrate_amount_total = Column(Numeric(5, 1))
    protein_amount_total = Column(Numeric(5, 1))
    fat_amount_total = Column(Numeric(5, 1))
    calories_amount_total = Column(Numeric(6, 1))
    carbohydrate_source_main = Column(String)
    carbohydrate_amount_main = Column(Numeric(5, 1))
    gi_score_of_main_carb = Column(Integer)
    food_names = Column(String)
    food_quantities = Column(Integer)


class UserLog(Base):
    __tablename__ = 'user_log'
    pk_user_log = Column(Integer, primary_key=True)
    fasting_glucose = Column(Integer)
    postprandial_glucose = Column(Integer)
    novorapid_dose = Column(Integer)
    hunger_status = Column(String)
    did_activity = Column(Boolean)
    minutes_after_activity = Column(Integer)
    meal_time = Column(TIMESTAMP)
    bed_time = Column(TIMESTAMP)
    wake_up_time = Column(TIMESTAMP)


class MealRecord(Base):
    __tablename__ = 'meal_record'
    record_id = Column(Integer, primary_key=True)
    fk_user = Column(Integer, ForeignKey('account.pk_user'))
    fk_meal_nutrition = Column(Integer, ForeignKey(
        'meal_nutrition.pk_meal_nutrition'))
    fk_user_log = Column(Integer, ForeignKey('user_log.pk_user_log'))
    user = relationship('Account')
    nutritions = relationship('MealNutrition')
    user_log = relationship('UserLog')

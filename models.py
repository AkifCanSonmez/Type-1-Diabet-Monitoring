from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base

#UserLog'a Lantus Column Ekle

class Account(Base):
    __tablename__ = 'account'
    pk_user = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    user_password = Column(String(30))
    email = Column(String(70), unique=True)
    created_on = Column(TIMESTAMP)
    last_login = Column(TIMESTAMP)
    body_fat = Column(Numeric(3, 1))
    age = Column(Integer)
    weight = Column(Numeric(4, 1))
    height = Column(Numeric(4, 1))
    activity = Column(String(20))

class FoodNutrition(Base):
    __tablename__ = 'food_nutritions'
    food_id = Column(Integer, primary_key=True)
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
    glycemic_index = Column(Integer)

class MealNutrition(Base):
    __tablename__ = 'meal_info_nutritions'
    pk_nutritions = Column(Integer, primary_key=True)
    carbohydrate_sources = Column(String)
    main_carbohydrate_source = Column(String)
    total_carbohydrate_amount = Column(Numeric(5, 2))
    main_carbohydrate_amount = Column(Numeric(5, 2))
    protein_amount = Column(Numeric(5, 2))
    fat_amount = Column(Numeric(5, 2))
    calories_amount = Column(Numeric(5, 2))

class UserLog(Base):
    __tablename__ = 'user_log'
    pk_userlog = Column(Integer, primary_key=True)
    lantus_dose = Column(Integer)
    bed_time = Column(TIMESTAMP)
    wake_up_time = Column(TIMESTAMP)
    meal_time = Column(TIMESTAMP)
    did_activity = Column(Boolean)
    minutes_after_activity = Column(Integer)
    hunger_status = Column(String)
    fasting_sugar_before_meal = Column(Integer)
    novorapid_dose_for_meal = Column(Integer)
    fullness_sugar_after_meal = Column(Integer)

class Meal(Base):
    __tablename__ = 'meal_info'
    pk_meal_id = Column(Integer, primary_key=True)
    fk_user = Column(Integer, ForeignKey('account.pk_user'))
    fk_nutritions = Column(Integer, ForeignKey('meal_info_nutritions.pk_nutritions'))
    fk_userlog = Column(Integer, ForeignKey('user_log.pk_userlog'))
    user = relationship('Account')
    nutritions = relationship('MealNutrition')
    user_log = relationship('UserLog')

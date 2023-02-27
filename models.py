from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from database import Base

class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key=True)
    carbohydrate_source = Column(String)
    total_carbohydrate_amount = Column(Integer)
    protein_amount = Column(Integer)
    fat_amount = Column(Integer)
    gi = Column(String)
    calorie_amount = Column(Integer)
    main_carbohydrate_amount = Column(Integer)

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
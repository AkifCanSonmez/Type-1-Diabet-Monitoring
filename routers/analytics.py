import sys
sys.path.append("..")

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
from io import BytesIO
import base64
from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.templating import Jinja2Templates
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import crud
from sqlalchemy.orm import Session
from database import SessionLocal
from . import auth
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="",
    tags=["health_analytics"],
    responses={401: {"user": "Not authorized"}}
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def draw_plotly(query):
    # Convert query to DataFrame
    df = pd.DataFrame(query, columns=["fasting_glucose", "carbohydrate_amount_total", "novorapid_dose", "carbohydrate_sources", "did_activity", "minutes_after_activity", "fk_user", "meal_time", "record_id"])
    
    fig = make_subplots()
    fig.add_trace(
        go.Scatter(x=df['record_id'], y=df['fasting_glucose'], mode='lines', name='Glucose Graphic', hovertemplate="Meal Time: %{x}<br>Fasting Glucose: %{y}<br><extra></extra>"),
    )

    # Add a red point where fasting_glucose is greater than 140
    x = df[df['fasting_glucose'] > 140]['record_id']
    y = df[df['fasting_glucose'] > 140]['fasting_glucose']
    marker_text = ["<br>".join(["Fasting Glucose: " +str(row['fasting_glucose']),"Carbohydrate Amount Total: "+str(row['carbohydrate_amount_total']), "Novorapid Dose: "+str(row['novorapid_dose']), "Carbohydrate Sources: "+str(row['carbohydrate_sources']), "Did Activity: "+str(row['did_activity']), "Minutes After Activity: "+str(row['minutes_after_activity'])]) for index, row in df[df['fasting_glucose'] > 140].iterrows()]
    fig.add_trace(
        go.Scatter(x=x, y=y, mode='markers', marker=dict(color='red', size=15), name='Glucose > 140', text=marker_text,
                   hovertemplate="Date: %{x|%d-%m-%Y}<extra></extra><br>%{text}<br>"),
    )

    fig.update_layout(
        title='Postprandial Glucose Over Time',
        xaxis_title='record_id',
        yaxis_title='Fasting Glucose',
        yaxis_tickmode='linear',
        yaxis_dtick=30,
        yaxis_range=[60, max(df['fasting_glucose'])+50],
        showlegend=True,
        legend=dict(x=0, y=1, bgcolor='rgba(255, 255, 255, 0.5)'),
        hovermode='closest',
        hoverlabel=dict(bgcolor='lightgreen', font_size=19,font_family="Rockwell")
    )
    
    return fig


@router.get("/home/analytics/glucose-analysis/")
async def show_glucose_analysis(request: Request, db:Session = Depends(get_db)):
    user = await auth.get_current_user(request)
    
    query = crud.get_mealRecord_for_glucoseAnalysis(db, user_id=user["id"], day=5)
    fig = draw_plotly(query)
    
    # encode figure to html
    fig_html = fig.to_html(full_html=False)
    
    avg_nutritions = crud.get_avg_nutritions(db, user_id=user["id"])

    #Bu Ayarlanacak
    avg_glucose = {"HbA1C": 5.6,"Average_Postprandial_Glucose": 160, "Average_Fasting_Glucose": 200}
    return templates.TemplateResponse("glucose_analysis.html", {"request": request, "fig_html": fig_html, "avg_glucose": avg_glucose, "avg_nutritions": avg_nutritions})










    
    '''# Define the data dictionaries
    # Verileri tanımla
    veriler = {'Aylar': ['Ocak', 'Subat', 'Mart'],
            'Kalori İhtiyaç': [2000, 2200, 1800],
            'Kalori Alım': [1800, 2100, 1900],
            'Protein İhtiyaç': [150, 170, 130],
            'Protein Alım': [140, 160, 120],
            'Karbonhidrat İhtiyaç': [300, 350, 250],
            'Karbonhidrat Alım': [280, 320, 240],
            'Yağ İhtiyaç': [100, 110, 90],
            'Yağ Alım': [90, 100, 80]}

    # DataFrame oluştur
    df = pd.DataFrame(veriler)
    df = df.set_index('Aylar')
    table = df.reset_index().values.tolist()
    #return templates.TemplateResponse("graphs2.html", {"request": request, "table": table})'''



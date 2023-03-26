from . import auth
from database import SessionLocal
from sqlalchemy.orm import Session
import crud
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException, Depends, status
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.append("..")


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="", tags=["health_analytics"], responses={401: {"user": "Not authorized"}}
)

# Dependency function to get database session


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Function to draw a Plotly graph given a query result


def draw_plotly(query):

    # Converting query to DataFrame
    df = pd.DataFrame(
        query,
        columns=[
            "postprandial_glucose",
            "carbohydrate_amount_total",
            "novorapid_dose",
            "carbohydrate_sources",
            "did_activity",
            "fk_user",
            "meal_time",
            "record_id",
        ],
    )

    # Create a new Plotly graph with multiple traces
    fig = make_subplots()

    # Add a trace for Postprandial glucose levels over time
    fig.add_trace(
        go.Scatter(
            x=df["meal_time"],
            y=df["postprandial_glucose"],
            mode="lines",
            name="Glucose Graphic",
            hovertemplate="Meal Time: %{x}<br>Postprandial Glucose: %{y}<br><extra></extra>",
        ),
    )

    # Adding green marker where Postprandial Glucose Value is Good
    x_green = df[(df["postprandial_glucose"] >= 70) & (df["postprandial_glucose"] <= 140)][
        "meal_time"
    ]
    y_green = df[(df["postprandial_glucose"] >= 70) & (df["postprandial_glucose"] <= 140)][
        "postprandial_glucose"
    ]
    marker_text = [
        "<br>".join(
            [
                "Postprandial Glucose: " + str(row["postprandial_glucose"]),
                "Carbohydrate Amount Total: " +
                str(row["carbohydrate_amount_total"]),
                "Novorapid Dose: " + str(row["novorapid_dose"]),
                "Carbohydrate Sources: " + str(row["carbohydrate_sources"]),
                "Did Activity: " + str(row["did_activity"]),
            ]
        )
        for index, row in df[
            (df["postprandial_glucose"] >= 70) & (
                df["postprandial_glucose"] <= 140)
        ].iterrows()
    ]
    fig.add_trace(
        go.Scatter(
            x=x_green,
            y=y_green,
            mode="markers",
            marker=dict(color="green", size=15),
            name="Glucose > 70 or < 140",
            text=marker_text,
            hovertemplate="Date: %{x|%d-%m-%Y}<extra></extra><br>%{text}<br>",
        ),
    )

    # Adding orange markers where postprandial_glucose is Bad
    x_orange = df[(df["postprandial_glucose"] >= 140) & (df["postprandial_glucose"] <= 200)][
        "meal_time"
    ]
    y_orange = df[(df["postprandial_glucose"] >= 140) & (df["postprandial_glucose"] <= 200)][
        "postprandial_glucose"
    ]
    marker_text_orange = [
        "<br>".join(
            [
                "Postprandial Glucose: " + str(row["postprandial_glucose"]),
                "Carbohydrate Amount Total: " +
                str(row["carbohydrate_amount_total"]),
                "Novorapid Dose: " + str(row["novorapid_dose"]),
                "Carbohydrate Sources: " + str(row["carbohydrate_sources"]),
                "Did Activity: " + str(row["did_activity"]),
            ]
        )
        for index, row in df[
            (df["postprandial_glucose"] >= 140) & (
                df["postprandial_glucose"] <= 200)
        ].iterrows()
    ]
    fig.add_trace(
        go.Scatter(
            x=x_orange,
            y=y_orange,
            mode="markers",
            marker=dict(color="orange", size=15),
            name="140 <= Glucose <= 200",
            text=marker_text_orange,
            hovertemplate="Date: %{x|%d-%m-%Y}<extra></extra><br>%{text}<br>",
        ),
    )

    # Adding red markers where Postprandial Glucose is too high or too low
    x_red = df[(df["postprandial_glucose"] > 200) | (df["postprandial_glucose"] <= 60)][
        "meal_time"
    ]
    y_red = df[(df["postprandial_glucose"] > 200) | (df["postprandial_glucose"] <= 60)][
        "postprandial_glucose"
    ]
    marker_text_red = [
        "<br>".join(
            [
                "Postprandial Glucose: " + str(row["postprandial_glucose"]),
                "Carbohydrate Amount Total: " +
                str(row["carbohydrate_amount_total"]),
                "Novorapid Dose: " + str(row["novorapid_dose"]),
                "Carbohydrate Sources: " + str(row["carbohydrate_sources"]),
                "Did Activity: " + str(row["did_activity"]),
            ]
        )
        for index, row in df[
            (df["postprandial_glucose"] > 200) | (
                df["postprandial_glucose"] <= 60)
        ].iterrows()
    ]
    fig.add_trace(
        go.Scatter(
            x=x_red,
            y=y_red,
            mode="markers",
            marker=dict(color="red", size=15),
            name="Glucose > 200 or < 60",
            text=marker_text_red,
            hovertemplate="Date: %{x|%d-%m-%Y}<extra></extra><br>%{text}<br>",
        ),
    )

    # Update the layout of the graph and return the updated figure
    fig.update_layout(
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),
        plot_bgcolor="beige",
        paper_bgcolor="beige",
        title="Postprandial Glucose Over Time",
        xaxis_title="Meal Date",
        yaxis_title="Postprandial Glucose",
        yaxis_tickmode="linear",
        yaxis_dtick=40,
        yaxis_range=[40, max(df["postprandial_glucose"]) + 40],
        showlegend=True,
        legend=dict(x=0, y=1, bgcolor="rgba(255, 255, 255, 0.5)"),
        hovermode="closest",
        hoverlabel=dict(bgcolor="lightgreen", font_size=19,
                        font_family="Rockwell"),
    )
    return fig


@router.get("/home/analytics/glucose-analysis/")
async def show_glucose_analysis(
    request: Request,
    db: Session = Depends(get_db),
    range: str = "30"
):
    user = await auth.get_current_user(request)

    # Define the range of days to retrieve the glucose data based on user input
    if range == "1":
        day = 1
    elif range == "7":
        day = 7
    elif range == "30":
        day = 30
    else:
        day = 90

    # Define the range options for the dropdown menu
    range_options = [
        {"label": "1 day", "value": "1"},
        {"label": "7 days", "value": "7"},
        {"label": "30 days", "value": "30"},
        {"label": "90 days", "value": "90"},
    ]

    # Define the default value for the dropdown menu
    range_value = {"label": f"{day} days", "value": str(day)}

    # 1: Retrieve glucose data for the selected range, create a plot, and convert it to HTML
    query = crud.get_mealRecord_for_glucoseAnalysis(
        db, user_id=user["id"], day=day)

    # If there is no any data that means user is new, raise HTTPException
    print(query)
    if len(query) == 0:
        raise HTTPException(
            status_code=404, detail="There is no data related to the user")

    fig = draw_plotly(query)
    fig_html = fig.to_html(full_html=False)

    # 2: Calculate the average glucose and HbA1C values for the past 3 months
    query, hba1c_list = crud.get_avg_blood_sugar(db, user_id=user["id"])

    # 3: Retrieve the average nutrition values for the past 3 months
    avg_nutritions = crud.get_avg_nutritions(db, user_id=user["id"])

    # Render glucose analysis template with necessary variables, and Return it
    return templates.TemplateResponse(
        "glucose_analysis.html",
        {
            "request": request,
            "fig_html": fig_html,
            "avg_nutritions": avg_nutritions,
            "query": query,
            "hba1c_list": hba1c_list,
            "range_options": range_options,
            "range_value": range_value,
        },
    )

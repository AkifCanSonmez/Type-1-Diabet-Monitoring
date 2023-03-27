from datetime import timedelta
from database import SessionLocal
from utils_common import convert_str_to_float, calculate_hba1c
from tables import MealNutrition, MealRecord, UserLog, Account
from decimal import Decimal
import datetime
import decimal
import tables
from sqlalchemy import or_, and_, func, extract
from sqlalchemy.orm import Session, joinedload, contains_eager
import pytz
import sys

sys.path.append("..")


def get_mealRecord_for_glucoseAnalysis(db: Session, user_id: int, day: int):

    query = (
        db.query(
            tables.UserLog.postprandial_glucose,
            tables.MealNutrition.carbohydrate_amount_total,
            tables.UserLog.novorapid_dose,
            tables.MealNutrition.carbohydrate_sources,
            tables.UserLog.did_activity,
            tables.MealRecord.fk_user,
            tables.UserLog.meal_time,
            tables.MealRecord.record_id,
        )
        .filter(
            tables.MealRecord.fk_user == user_id,
            tables.UserLog.meal_time >= datetime.datetime.now() - timedelta(days=day),
        )
        .join(
            tables.MealRecord,
            tables.MealRecord.fk_user_log == tables.UserLog.pk_user_log,
        )
        .join(
            tables.MealNutrition,
            tables.MealRecord.fk_meal_nutrition
            == tables.MealNutrition.pk_meal_nutrition,
        )
        .order_by(tables.UserLog.meal_time.desc())
        .all()
    )
    return query


def get_avg_nutritions(db: Session, user_id: int):
    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=60)
    query = (
        db.query(
            func.date_trunc("month", tables.UserLog.meal_time).label("month"),
            func.round(func.avg(tables.MealNutrition.calories_amount_total)).label(
                "avg_calories"
            ),
            func.round(func.avg(tables.MealNutrition.carbohydrate_amount_main)).label(
                "avg_carbs"
            ),
            func.round(func.avg(tables.MealNutrition.protein_amount_total)).label(
                "avg_protein"
            ),
            func.round(func.avg(tables.MealNutrition.fat_amount_total)).label(
                "avg_fat"
            ),
        )
        .join(
            tables.MealRecord,
            tables.MealRecord.fk_user_log == tables.UserLog.pk_user_log,
        )
        .filter(
            tables.MealNutrition.pk_meal_nutrition
            == tables.MealRecord.fk_meal_nutrition,
            tables.MealRecord.fk_user == user_id,
            tables.UserLog.meal_time >= three_months_ago,
        )
        .group_by("month")
        .all()
    )

    return query


def get_avg_blood_sugar(db: Session, user_id: int):
    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)
    query = (
        db.query(
            func.date_trunc("month", tables.UserLog.meal_time).label("month"),
            func.round(func.avg(tables.UserLog.fasting_glucose)).label(
                "avg_fasting_glucose"
            ),
            func.round(func.avg(tables.UserLog.postprandial_glucose)).label(
                "avg_postprandial_glucose"
            ),
        )
        .join(
            tables.MealRecord,
            tables.MealRecord.fk_user_log == tables.UserLog.pk_user_log,
        )
        .filter(
            tables.MealNutrition.pk_meal_nutrition
            == tables.MealRecord.fk_meal_nutrition,
            tables.MealRecord.fk_user == user_id,
            tables.UserLog.meal_time >= three_months_ago,
        )
        .group_by("month")
        .all()
    )

    hba1c_list = calculate_hba1c(query)
    return (query, hba1c_list)


def get_nutritional_informations(db: Session, foods: list):
    query_nutrition_values = (
        db.query(tables.NutritionDB)
        .filter(or_(*[tables.NutritionDB.food_name == food for food in foods]))
        .all()
    )
    return query_nutrition_values


def get_bed_time_today(db: Session, current_user_id: int):

    last_row = (
        db.query(tables.UserLog)
        .join(tables.MealRecord)
        .filter(tables.MealRecord.fk_user == current_user_id)
        .order_by(tables.UserLog.pk_user_log.desc())
        .first()
    )

    if (
        last_row is None
        or last_row.bed_time is None
        or last_row.bed_time.date() != datetime.date.today()
    ):
        return None
    else:
        return "There is already bed time for today"


def get_last_meal_record(db: Session, user_id: int):
    last_meal_record = (
        db.query(MealRecord)
        .filter(MealRecord.fk_user == user_id)
        .order_by(MealRecord.record_id.desc())
        .first()
    )
    return last_meal_record


def delete_missing_data(db: Session, user_id: int):
    last_meal_record = (
        db.query(MealRecord)
        .filter(MealRecord.fk_user == user_id)
        .order_by(MealRecord.record_id.desc())
        .first()
    )
    db.delete(last_meal_record)
    db.commit()


def get_missing_new_meal(db: Session, user_id: int):
    latest_meal_record = (
        db.query(tables.MealRecord)
        .options(joinedload(tables.MealRecord.nutritions))
        .filter(tables.MealRecord.fk_user == user_id)
        .order_by(tables.MealRecord.record_id.desc())
        .first()
    )

    if (latest_meal_record is not None
            and latest_meal_record.fk_user_log == None):

        foods = latest_meal_record.nutritions.food_names 
        quantities = latest_meal_record.nutritions.food_quantities
        last_meal_nutrition_information = {}

        if "," in foods:
            foods = foods.split(",")
            quantities = quantities.split(",")

            for food, quantity in zip(foods, quantities):
                last_meal_nutrition_information[food] = int(quantity)
        else:
            last_meal_nutrition_information[foods] = int(quantities)

        return last_meal_nutrition_information
    else:
        return None


def get_missing_postprandial_glucose(db: Session, user_id: int):
    latest_meal_record = (
        db.query(tables.MealRecord)
        .filter(tables.MealRecord.fk_user == user_id)
        .order_by(tables.MealRecord.record_id.desc())
        .first()
    )

    current_time = datetime.datetime.utcnow()
    if (latest_meal_record is not None
            and latest_meal_record.user_log.postprandial_glucose == None):
        return latest_meal_record
    else:
        return None


def get_missing_novorapid_dose(db: Session, user_id: int):
    latest_meal_record = (
        db.query(tables.MealRecord)
        .filter(tables.MealRecord.fk_user == user_id)
        .order_by(tables.MealRecord.record_id.desc())
        .first()
    )
    if (latest_meal_record is not None
            and latest_meal_record.user_log.novorapid_dose == None):
        return latest_meal_record
    else:
        return None


def update_postprandial_glucose_row(db: Session, user_id, postprandial_glucose):
    latest_meal_record = (
        db.query(tables.MealRecord)
        .filter(tables.MealRecord.fk_user == user_id)
        .order_by(tables.MealRecord.record_id.desc())
        .first()
    )
    latest_meal_record.user_log.postprandial_glucose = postprandial_glucose
    db.commit()
    return "Completed"


def update_novorapid_dose(db: Session, user_id, novorapid_dose):
    latest_meal_record = (
        db.query(tables.MealRecord)
        .filter(tables.MealRecord.fk_user == user_id)
        .order_by(tables.MealRecord.record_id.desc())
        .first()
    )
    latest_meal_record.user_log.novorapid_dose = novorapid_dose
    db.commit()


def get_meal_suggestions(db: Session, fasting_glucose, meal_time, activity_status, user_id):

    meal_time_hour, meal_time_minute = meal_time.split(":")
    meal_time_hour = int(meal_time_hour)

    activity_status = True if activity_status == "yes" else False

    data_1 = (
        db.query(MealRecord)
        .order_by(MealRecord.record_id.desc())
        .join(MealRecord.nutritions)
        .join(MealRecord.user_log)
        .options(
            contains_eager(MealRecord.nutritions), contains_eager(
                MealRecord.user_log)
        )
        .filter(
            and_(
                MealRecord.fk_user == user_id,
                UserLog.fasting_glucose.between(
                    int(fasting_glucose * 0.85), int(fasting_glucose * 1.15)
                ),
                UserLog.postprandial_glucose.between(70, 150),
                extract("hour", UserLog.meal_time).between(
                    meal_time_hour - 2, meal_time_hour + 2
                ),
                (
                    UserLog.did_activity == activity_status
                )
            )
        )
        .limit(3)
        .all()
    )

    data_2 = (
        db.query(MealRecord)
        .order_by(MealRecord.record_id.desc())
        .join(MealRecord.nutritions)
        .join(MealRecord.user_log)
        .options(
            contains_eager(MealRecord.nutritions), contains_eager(
                MealRecord.user_log)
        )
        .filter(
            and_(
                MealRecord.fk_user == user_id,
                UserLog.fasting_glucose.between(
                    int(fasting_glucose * 0.85), int(fasting_glucose * 1.15)
                ),
                UserLog.postprandial_glucose > 160,
                extract("hour", UserLog.meal_time).between(
                    meal_time_hour - 2, meal_time_hour + 2
                ),
                (
                    UserLog.did_activity == activity_status

                )
            )
        )
        .limit(3)
        .all()
    )

    data_w_high_glucose = {
        "meal_time": [],
        "food_names": [],
        "food_quantities": [],
        "carbohydrate_amount_total": [],
        "fasting_glucose": [],
        "novorapid_dose": [],
        "postprandial_glucose": [],
        "did_activity": [],
        "minutes_after_activity": []
    }

    data_w_good_glucose = {
        "meal_time": [],
        "food_names": [],
        "food_quantities": [],
        "carbohydrate_amount_total": [],
        "fasting_glucose": [],
        "novorapid_dose": [],
        "postprandial_glucose": [],
        "did_activity": [],
        "minutes_after_activity": []
    }

    for data in data_1:
        data_w_good_glucose["meal_time"].append(data.user_log.meal_time)
        data_w_good_glucose["food_names"].append(data.nutritions.food_names)
        data_w_good_glucose["food_quantities"].append(
            data.nutritions.food_quantities)
        data_w_good_glucose["carbohydrate_amount_total"].append(
            data.nutritions.carbohydrate_amount_total
        )
        data_w_good_glucose["fasting_glucose"].append(
            data.user_log.fasting_glucose)
        data_w_good_glucose["novorapid_dose"].append(
            data.user_log.novorapid_dose)
        data_w_good_glucose["postprandial_glucose"].append(
            data.user_log.postprandial_glucose
        )
        data_w_good_glucose["did_activity"].append(data.user_log.did_activity)
        data_w_good_glucose["minutes_after_activity"].append(
            data.user_log.minutes_after_activity)

    for data in data_2:
        data_w_high_glucose["meal_time"].append(data.user_log.meal_time)
        data_w_high_glucose["food_names"].append(data.nutritions.food_names)
        data_w_high_glucose["food_quantities"].append(
            data.nutritions.food_quantities)
        data_w_high_glucose["carbohydrate_amount_total"].append(
            data.nutritions.carbohydrate_amount_total
        )
        data_w_high_glucose["fasting_glucose"].append(
            data.user_log.fasting_glucose)
        data_w_high_glucose["novorapid_dose"].append(
            data.user_log.novorapid_dose)
        data_w_high_glucose["postprandial_glucose"].append(
            data.user_log.postprandial_glucose
        )
        data_w_high_glucose["did_activity"].append(data.user_log.did_activity)
        data_w_high_glucose["minutes_after_activity"].append(
            data.user_log.minutes_after_activity)

    return (data_w_good_glucose, data_w_high_glucose)


def process_nutrition_inputs(db: Session, foods_n_amounts: dict):
    query_nutrition_values = get_nutritional_informations(
        db, foods_n_amounts.keys())

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
            self.food_names: str = ""
            self.foods_quantities: str = ""

    cols = columns_nutritions()

    # Used for detecting carb sources, max carb source(main_carb) & gi of main carb
    carbs_of_foods: dict = {}

    # Calculating
    for query in query_nutrition_values:
        food = query.food_name
        food_amount = float(foods_n_amounts[food])

        # Getting Foods' carb-protein-fat nutritions values in 100g
        # !Nutrition values are stored in str type like '60(g)', '17(g)' etc.
        carb_100, protein_100, fat_100 = convert_str_to_float(
            query.carbohydrate_100g, query.protein_100g, query.fat_100g
        )

        # Calculating nutrition values for meal food
        food_carb_amount = carb_100 * (food_amount / 100)
        cols.carbohydrate_amount_total += food_carb_amount
        cols.protein_amount_total += protein_100 * (food_amount / 100)
        cols.fat_amount_total += fat_100 * (food_amount / 100)
        cols.calories_amount_total += float(query.calories_100g) * \
            (food_amount / 100)
        carbs_of_foods[food] = carb_100 * (food_amount / 100)

        # Main carbohydrate will be food with max carbs amount
        if food_carb_amount > cols.carbohydrate_amount_main:
            cols.carbohydrate_amount_main = food_carb_amount
            cols.carbohydrate_source_main = food

    # carbs_of_foods dictionary sorted, in this way carbohydrate_sources will order in max to min carb source(I need this on GSM algorithm)
    # Adding carbohydrates that are equal to 25% of the total amount of carbohydrates
    carbs_of_foods = dict(
        sorted(carbs_of_foods.items(), key=lambda x: x[1], reverse=True)
    )
    carbs_source_list = []
    percentage = 0.25
    for food in carbs_of_foods:
        food_carb_value = carbs_of_foods[food]
        total_carb_value = cols.carbohydrate_amount_total
        if food_carb_value >= total_carb_value * percentage:
            carbs_source_list.append(food)
    cols.carbohydrate_sources = ",".join(carbs_source_list)

    # gi_score will be main carb's gi score
    cols.gi_score_of_main_carb = (
        db.query(tables.NutritionDB.glycemic_index)
        .filter(tables.NutritionDB.food_name == cols.carbohydrate_source_main)
        .first()[0]
    )

    # converting objects to two comma-separated strings and adding them to cols
    cols.food_names = ",".join(foods_n_amounts.keys())
    cols.foods_quantities = ",".join(foods_n_amounts.values())

    return cols


def process_user_log_inputs(db: Session, user_log):

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

    col.did_activity = True if user_log["did-activity"] == "yes" else False
    col.hunger_status = user_log["hunger-status"]
    col.fasting_glucose = user_log["fasting-glucose"]

    if col.did_activity:
        act_end = datetime.datetime.strptime(
            user_log["activity-end-time"], "%H:%M"
        ).time()
        now = datetime.datetime.utcnow().replace(
            second=0, microsecond=0
        ).time()
        col.minutes_after_activity = (
            ((now.hour - act_end.hour) * 60) + now.minute - act_end.minute
        )
    else:
        col.minutes_after_activity = (
            1  # This is Default value for avoiding mathematical operations errors
        )
        
    col.meal_time = datetime.datetime.utcnow().replace(microsecond=0)
    print(col.meal_time)

    # Kullanıcında Bed Time input'u aynı gün içerisinde bed time girilmemişse geliyor
    if "Bed Time" in user_log.keys():
        bed_time = datetime.datetime.strptime(
            user_log["Bed Time"], "%H:%M"
        ).time()
        wake_up_time = datetime.datetime.strptime(
            user_log["Wake Up Time"], "%H:%M"
        ).time()
        now = datetime.datetime.utcnow()

        # Getting TIMESTAMP value
        col.bed_time = datetime.datetime.combine(now.date(), bed_time)
        col.wake_up_time = datetime.datetime.combine(now.date(), wake_up_time)

    else:
        # If there is bed&wake up time for same day in db, use this for new row
        last_row = (
            db.query(tables.UserLog).order_by(
                tables.UserLog.pk_user_log.desc()
            ).first()
        )
        col.bed_time = last_row.bed_time
        col.wake_up_time = last_row.wake_up_time

    return col

def populate_todo_user_log(todo_model, cols):
    todo_model.bed_time = cols.bed_time
    todo_model.did_activity = cols.did_activity
    todo_model.fasting_glucose = cols.fasting_glucose
    todo_model.hunger_status = cols.hunger_status
    todo_model.meal_time = cols.meal_time
    todo_model.minutes_after_activity = cols.minutes_after_activity
    todo_model.wake_up_time = cols.wake_up_time


def populate_meal_nutrition(todo_model, cols):
    todo_model.carbohydrate_amount_total = decimal.Decimal(
        str(cols.carbohydrate_amount_total)
    ).quantize(decimal.Decimal(".1"))
    todo_model.carbohydrate_amount_main = decimal.Decimal(
        str(cols.carbohydrate_amount_main)
    ).quantize(decimal.Decimal(".1"))
    todo_model.calories_amount_total = decimal.Decimal(
        str(cols.calories_amount_total)
    ).quantize(decimal.Decimal(".1"))
    todo_model.carbohydrate_source_main = cols.carbohydrate_source_main
    todo_model.carbohydrate_sources = cols.carbohydrate_sources
    todo_model.fat_amount_total = decimal.Decimal(str(cols.fat_amount_total)).quantize(
        decimal.Decimal(".1")
    )
    todo_model.gi_score_of_main_carb = cols.gi_score_of_main_carb
    todo_model.protein_amount_total = decimal.Decimal(
        str(cols.protein_amount_total)
    ).quantize(decimal.Decimal(".1"))
    todo_model.food_names = cols.food_names
    todo_model.food_quantities = cols.foods_quantities


def add_todo_meal_nutrition(db: Session, foods_n_amounts):

    # Create a new MealNutrition object and populate it with the nutrition values calculated from the inputs
    todo_model = tables.MealNutrition()

    # Calculate the nutrition values for the meal and populate the todo_model object
    cols = process_nutrition_inputs(db, foods_n_amounts)
    populate_meal_nutrition(todo_model, cols)

    # Add the meal nutrition objects to the meal_nutrition table and return its PK
    db.add(todo_model)
    db.commit()
    return todo_model.pk_meal_nutrition


def add_todo_user_log(db: Session, user_log):
    todo_model = tables.UserLog()
    cols = process_user_log_inputs(db, user_log)
    populate_todo_user_log(todo_model, cols)

    db.add(todo_model)
    db.commit()
    return todo_model.pk_user_log


def add_new_meal(db: Session, user, meal_foods_amounts, user_log):
    pk_user = user["id"]
    pk_meal_nutrition = add_todo_meal_nutrition(db, meal_foods_amounts)
    pk_user_log = add_todo_user_log(db, user_log)

    todo_model = tables.MealRecord()
    todo_model.fk_meal_nutrition = pk_meal_nutrition
    todo_model.fk_user = pk_user
    todo_model.fk_user_log = pk_user_log
    db.add(todo_model)
    db.commit()
    return {
        "KEYS": {
            "PK_MealNutrition": pk_meal_nutrition,
            "PK_UserLog": pk_user_log,
            "PK_User": pk_user,
            "FK_MealNutrition": todo_model.fk_meal_nutrition,
            "FK_UserLog": todo_model.fk_user_log,
            "FK_User": todo_model.fk_user,
        }
    }


def save_nutritions_and_exit(db: Session, user, foods_n_amounts):
    pk_user = user["id"]
    pk_meal_nutrition = add_todo_meal_nutrition(db, foods_n_amounts)

    todo_model = tables.MealRecord()
    todo_model.fk_meal_nutrition = pk_meal_nutrition
    todo_model.fk_user = pk_user
    db.add(todo_model)
    db.commit()


def update_new_meal_user_log(db: Session, user, user_log):
    pk_user = user["id"]
    todo_model = get_last_meal_record(db, pk_user)

    pk_user_log = add_todo_user_log(db, user_log)
    todo_model.fk_user_log = pk_user_log
    db.commit()
    return


def get_similar_meals(db: Session, user_id):
    new_meal = db.query(MealRecord).\
        filter(MealRecord.fk_user == user_id).\
        order_by(MealRecord.record_id.desc()).first()

    meal_records = db.query(MealRecord).\
        join(MealRecord.nutritions).\
        join(MealRecord.user_log).\
        options(
            contains_eager(MealRecord.nutritions).load_only(
                MealNutrition.carbohydrate_sources, MealNutrition.carbohydrate_amount_total),
            contains_eager(MealRecord.user_log).load_only(
                UserLog.fasting_glucose, UserLog.postprandial_glucose, UserLog.novorapid_dose)
    ).\
        filter(MealRecord.fk_user == user_id, UserLog.did_activity == new_meal.user_log.did_activity,
               UserLog.postprandial_glucose != None, UserLog.minutes_after_activity <= (
                   new_meal.user_log.minutes_after_activity * 1.25),
               MealRecord.record_id != new_meal.record_id)

    if len(meal_records.all()) == 0:
        return None

    for seq in range(4):
        if seq == 0:
            # Carb sources and main equal and total carb %15 main carb %15
            data = meal_records.filter(
                and_(MealNutrition.carbohydrate_source_main == new_meal.nutritions.carbohydrate_source_main,
                     MealNutrition.carbohydrate_sources == new_meal.nutritions.carbohydrate_sources,
                     func.abs(new_meal.nutritions.carbohydrate_amount_total -
                              MealNutrition.carbohydrate_amount_total)
                     <= (new_meal.nutritions.carbohydrate_amount_total * Decimal("0.10")),
                     func.abs(new_meal.nutritions.carbohydrate_amount_main -
                              MealNutrition.carbohydrate_amount_main)
                     <= (new_meal.nutritions.carbohydrate_amount_main * Decimal("0.10")),
                     func.abs(UserLog.postprandial_glucose -
                              UserLog.fasting_glucose) <= (UserLog.fasting_glucose * 0.15)
                     )
            )

            if data.count() > 0:
                data = data.order_by(
                    func.abs(UserLog.fasting_glucose -
                             new_meal.user_log.fasting_glucose)
                )
                similar_meals = data.limit(3).all()
                break
            else:
                continue

        elif seq == 1:
            # Carb sources main equal and total carb %15 main carb %15
            data = meal_records.filter(
                and_(MealNutrition.carbohydrate_source_main == new_meal.nutritions.carbohydrate_source_main,
                     func.abs(new_meal.nutritions.carbohydrate_amount_total -
                              MealNutrition.carbohydrate_amount_total)
                     <= (new_meal.nutritions.carbohydrate_amount_total * Decimal("0.10")),
                     func.abs(new_meal.nutritions.carbohydrate_amount_main -
                              MealNutrition.carbohydrate_amount_main)
                     <= (new_meal.nutritions.carbohydrate_amount_main * Decimal("0.10")),
                     func.abs(UserLog.postprandial_glucose -
                              UserLog.fasting_glucose) <= (UserLog.fasting_glucose * 0.15)
                     )
            )

            if data.count() > 0:
                data = data.order_by(
                    func.abs(UserLog.fasting_glucose -
                             new_meal.user_log.fasting_glucose)
                )
                similar_meals = data.limit(3).all()
                break
            else:
                continue

        elif seq == 2:
            # Carb source main equal and carb amount total %15
            data = meal_records.filter(
                and_(MealNutrition.carbohydrate_source_main == new_meal.nutritions.carbohydrate_source_main,
                     func.abs(new_meal.nutritions.carbohydrate_amount_total -
                              MealNutrition.carbohydrate_amount_total)
                     <= (new_meal.nutritions.carbohydrate_amount_total * Decimal("0.10")),
                     func.abs(UserLog.postprandial_glucose -
                              UserLog.fasting_glucose) <= (UserLog.fasting_glucose * 0.15)
                     )
            )

            if data.count() > 0:
                data = data.order_by(
                    func.abs(UserLog.fasting_glucose -
                             new_meal.user_log.fasting_glucose)
                )
                similar_meals = data.limit(3).all()
                break
            else:
                continue

        elif seq == 3:

            # Carb sources main not equal, so getting data where gi score in between new_meal gi score %90 percent
            data = meal_records.filter(
                and_(
                    MealNutrition.carbohydrate_source_main != new_meal.nutritions.carbohydrate_source_main,
                    or_(
                        func.abs(new_meal.nutritions.gi_score_of_main_carb -
                                 MealNutrition.gi_score_of_main_carb)
                        <= (new_meal.nutritions.gi_score_of_main_carb * 0.15)
                    ),
                    or_(
                        func.abs(new_meal.nutritions.carbohydrate_amount_total -
                                 MealNutrition.carbohydrate_amount_total)
                        <= (new_meal.nutritions.carbohydrate_amount_total * Decimal("0.10"))
                    ),
                    func.abs(UserLog.postprandial_glucose -
                             UserLog.fasting_glucose) <= (UserLog.fasting_glucose * 0.15)
                )
            )

            if data.count() > 0:
                data = data.order_by(
                    func.abs(UserLog.fasting_glucose -
                             new_meal.user_log.fasting_glucose)
                )

                similar_meals = data.limit(3).all()
                break
            else:
                similar_meals = False

    return similar_meals

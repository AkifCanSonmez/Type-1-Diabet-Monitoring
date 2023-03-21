# Type-1-Diabetes-Monitoring

## Table of Contents
1. [Why I Created This Program](#why-i-created-this-program)
2. [How the Program Works](#how-the-program-works)
    1. [Real-time Meal-based Functions](#real-time-meal-based-functions)
    2. [Analyses](#analyses)
    3. [Meal Recommendations](#meal-recommendations)
3. [What Does This Algorithm Do?](#what-does-this-algorithm-do)
4. [How the Algorithm Works](#how-the-algorithm-works)

Why I Created This Program

One of the biggest challenges faced by individuals with Type 1 diabetes is managing blood sugar fluctuations. This issue typically arises when patients are unable to accurately calculate the insulin dosage required before a meal. This problem can lead to dangerous situations, such as hypoglycemia.

The most widely practiced method to address this issue today is known as carbohydrate counting. This method involves patients recording data such as pre- and post-meal blood sugar levels and the amount of carbohydrates consumed in a journal. Through trial and error, the patient's insulin sensitivity is determined based on the amount of carbohydrates consumed and the corresponding insulin dosage. A diet plan is then tailored to the patient's needs.

However, this method may not yield effective results if the patient's diet includes a wide range of carbohydrate quantities. The primary reason for this is the non-linear relationship between insulin and carbohydrates, making it difficult to draw conclusions as the amount of data increases. As a result, patients are often advised to follow a diet plan with limited meal options containing fixed carbohydrate amounts.

Other factors influencing insulin sensitivity include sleep patterns, meal intervals and timing, the glycemic index of carbohydrate sources, pre-meal fasting levels, and physical activity levels. However, patients may struggle to consistently record such parameters, leading to these factors being overlooked. This can result in an inadequate consideration of factors affecting insulin resistance.

The aim of this project is to facilitate practical data collection for patients and to ensure that factors believed to impact insulin dosage, but often overlooked, are also recorded. By analyzing this data, both pre-meal and on a weekly or monthly basis, blood sugar fluctuations can be better controlled. The provided analyses will enable healthcare professionals to work with a broader range of data. Additionally, through simple analyses, patients will be able to collaborate with healthcare professionals in determining their required insulin dosage.  

How the Program Works

The program has three main functions: 1) real-time meal-based operations, 2) weekly and monthly data analysis, and 3) meal recommendations for users.

Real-time Meal-based Functions:

The user weighs and takes a photo of all raw ingredients before a meal. The photo is processed in the back-end, and food detection is performed using a YOLOv5 model to identify the ingredients. The user then enters the weight of each ingredient, and the meal information is saved. After the meal is prepared, the user enters pre-meal blood sugar, hunger level, and activity status. These data points are processed, and up to 3 similar meals from the database are retrieved and displayed along with the new meal information. For Type 1 diabetic bodybuilders, calorie, carbohydrate, protein, and fat amounts are also provided. The user decides the insulin dosage, enters it, and adds a new meal. Two hours after the meal, the user enters their post-meal blood sugar, completing the data entry.

Analyses:

Three main analyses are performed. 1) A graph displays the user's post-meal blood sugar levels within a specified date range. Points on the graph are marked with green (good), orange (low risk), or red (high risk) markers. Users can click on markers to access general information about the meal, helping them adjust insulin dosages for meals with risky blood sugar levels.

The second analysis shows the patient's 3-month pre- and post-meal blood sugar levels and an estimated HbA1c value calculated using an algorithm. Although not exact, this HbA1c value generally provides accurate estimations.

The third analysis is for Type 1 diabetic bodybuilders, providing a one-month nutrition analysis to track calorie and nutrient intake for weight gain or loss goals.

Meal Recommendations:

The user inputs current blood sugar, time, and activity levels, and the back-end processes this information to display up to 5 meals with excellent post-meal blood sugar results from the database. The user can prepare a new meal using these recommendations. Additionally, up to 5 meals with poor post-meal blood sugar results are shown. The user can repeat these meals with an adjusted insulin dosage and save them to the database. This way, the user can determine the appropriate insulin dosage for similar meals in the future and avoid hyperglycemia risk.

What Does This Algorithm Do?

As mentioned earlier, there are many factors that affect insulin sensitivity. In particular, the glycemic index of foods and pre-meal activity levels play significant roles in determining the required insulin dosage.

After exercise, glucose levels in the body decrease, and the number of insulin receptors in muscle cells increases. This reduces insulin resistance and increases insulin sensitivity. As a result, a patient may require less insulin for a meal with identical nutritional values when they exercise compared to when they don't.

Another crucial factor is the glycemic index. Foods with a high glycemic index raise blood sugar levels rapidly and may necessitate more insulin. In contrast, foods with a low glycemic index are digested more slowly, potentially leading to a slower increase in blood sugar and requiring less insulin. Therefore, the insulin requirements for bulgur and rice may differ even if they have the same carbohydrate content.

Several other factors, such as meal timing, sleep and wake-up times, and pre-meal fasting levels, also impact insulin sensitivity. This program records these factors and displays data with meal information similar to the user's current meal to help them calculate their pre-meal insulin needs. This makes it easier to prevent dangerous situations like hypoglycemia.

How the Algorithm Works

The user's most recently added meal is retrieved from the database. To do this, the MealRecord table is filtered based on the user's ID, and the latest record is selected.
To choose similar meals, the MealRecord, MealNutrition, and UserLog tables are merged. This merging process is performed to select meals similar to the user's most recent meal. In this step, the three tables are combined, and the relevant columns are selected.
The following features are considered when selecting similar meals:
• Sources of carbohydrates
• Total carbohydrate amount
• Main carbohydrate amount
• Fasting and postprandial glucose values
• Type and duration of activity
• Differences between carbohydrate sources and amounts in similar meals and the last meal
The selection of similar meals is carried out sequentially based on different scenarios. Each scenario selects similar meals based on specific features. The scenarios include:
• Meals with completely matching carbohydrate sources and amounts are chosen. In this scenario, a difference of less than 10% in the main carbohydrate amount is expected.
• Meals with matching main carbohydrate sources are chosen. In this scenario, a difference of less than 10% in the main carbohydrate amount is expected.
• Meals with only matching carbohydrate amounts are chosen. In this scenario, a difference of less than 10% in the total carbohydrate amount is expected.
• Meals with different main carbohydrate sources are chosen. In this scenario, a difference of less than 15% in glycemic indices of the main carbohydrate sources is expected. Additionally, a difference of less than 10% in the total carbohydrate amount is expected.
The selected similar meals are stored in a dictionary, considering features like carbohydrate sources, total carbohydrate amount, fasting glucose value, novorapid dose, and postprandial glucose value.
Finally, the dictionary is returned to display similar meals to the user.
These steps ensure that the user's most recently added meal is compared with other meals in the database, and similar meals are selected, allowing the user to decide how much insulin to inject based on similar meals. In conclusion, this code serves as a tool to help users determine their insulin dosage. By selecting similar meals, users are provided with suggestions, enabling them to make more accurate decisions for diabetes management.

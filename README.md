# Type 1 Diabetes Monitoring

## Table of Contents
1. [Why I Created This Program](#why-i-created-this-program)
2. [How the Program Works](#how-the-program-works)
    1. [Real-time Meal-based Functions](#real-time-meal-based-functions)
    2. [Analyses](#analyses)
    3. [Meal Recommendations](#meal-recommendations)
3. [What Does Get Similar Meals Algorithm Do?](#what-does-get-similar-meals-algorithm-do)
4. [How the Get Similar Meals Algorithm Works](#how-the-get-similar-meals-algorithm-works)
5. [Technologies Used](#technologies-used)
6. [Try App with EC2 IP](#try-app-with-ec2-ip)
7. [Video Description](#video-description)




## Why I Created This Program

One of the biggest challenges faced by individuals with Type 1 diabetes is managing blood sugar fluctuations. This issue typically arises when patients are unable to accurately calculate the insulin dosage required before a meal. This problem can lead to dangerous situations, such as hypoglycemia.

The most widely practiced method to address this issue today is known as carbohydrate counting. This method involves patients recording data such as pre- and post-meal blood sugar levels and the amount of carbohydrates consumed in a journal. Through trial and error, the patient's insulin sensitivity is determined based on the amount of carbohydrates consumed and the corresponding insulin dosage. A diet plan is then tailored to the patient's needs.

However, this method may not yield effective results if the patient's diet includes a wide range of carbohydrate quantities. The primary reason for this is the non-linear relationship between insulin and carbohydrates, making it difficult to draw conclusions as the amount of data increases. As a result, patients are often advised to follow a diet plan with limited meal options containing fixed carbohydrate amounts.

Other factors influencing insulin sensitivity include sleep patterns, meal intervals and timing, the glycemic index of carbohydrate sources, pre-meal fasting levels, and physical activity levels. However, patients may struggle to consistently record such parameters, leading to these factors being overlooked. This can result in an inadequate consideration of factors affecting insulin resistance.

The aim of this project is to facilitate practical data collection for patients and to ensure that factors believed to impact insulin dosage, but often overlooked, are also recorded. By analyzing this data, both pre-meal and on a weekly or monthly basis, blood sugar fluctuations can be better controlled. The provided analyses will enable healthcare professionals to work with a broader range of data. Additionally, through simple analyses, patients will be able to collaborate with healthcare professionals in determining their required insulin dosage.  

## How the Program Works

The program has three main functions: 1) real-time meal-based operations, 2) weekly and monthly data analysis, and 3) meal recommendations for users.

### Real-time Meal-based Functions

The user weighs and takes a photo of all raw ingredients before a meal. The photo is processed in the back-end, and food detection is performed using a YOLOv5 model to identify the ingredients. The user then enters the weight of each ingredient, and the meal information is saved. After the meal is prepared, the user enters pre-meal blood sugar, hunger level, and activity status. These data points are processed, and up to 3 similar meals from the database are retrieved and displayed along with the new meal information. For Type 1 diabetic bodybuilders, calorie, carbohydrate, protein, and fat amounts are also provided. The user decides the insulin dosage, enters it, and adds a new meal. Two hours after the meal, the user enters their post-meal blood sugar, completing the data entry.

### Analyses

Three main analyses are performed. 1) A graph displays the user's post-meal blood sugar levels within a specified date range. Points on the graph are marked with green (good), orange (low risk), or red (high risk) markers. Users can click on markers to access general information about the meal, helping them adjust insulin dosages for meals with risky blood sugar levels.

The second analysis shows the patient's 3-month pre- and post-meal blood sugar levels and an estimated HbA1c value calculated using an algorithm. Although not exact, this HbA1c value generally provides accurate estimations.

The third analysis is for Type 1 diabetic bodybuilders, providing a one-month nutrition analysis to track calorie and nutrient intake for weight gain or loss goals.

### Meal Recommendations

The user inputs current blood sugar, time, and activity levels, and the back-end processes this information to display up to 5 meals with excellent post-meal blood sugar results from the database. The user can prepare a new meal using these recommendations. Additionally, up to 5 meals with poor post-meal blood sugar results are shown. The user can repeat these meals with an adjusted insulin dosage and save them to the database. This way, the user can determine the appropriate insulin dosage for similar meals in the future and avoid hyperglycemia risk.

## What Does Get Similar Meals Algorithm Do?

As mentioned earlier, there are many factors that affect insulin sensitivity. In particular, the glycemic index of foods and pre-meal activity levels play significant roles in determining the required insulin dosage.

After exercise, glucose levels in the body decrease, and the number of insulin receptors in muscle cells increases. This reduces insulin resistance and increases insulin sensitivity. As a result, a patient may require less insulin for a meal with identical nutritional values when they exercise compared to when they don't.

Another crucial factor is the glycemic index. Foods with a high glycemic index raise blood sugar levels rapidly and may necessitate more insulin. In contrast, foods with a low glycemic index are digested more slowly, potentially leading to a slower increase in blood sugar and requiring less insulin. Therefore, the insulin requirements for bulgur and rice may differ even if they have the same carbohydrate content.

Several other factors, such as meal timing, sleep and wake-up times, and pre-meal fasting levels, also impact insulin sensitivity. This program records these factors and displays data with meal information similar to the user's current meal to help them calculate their pre-meal insulin needs. This makes it easier to prevent dangerous situations like hypoglycemia.

## How the Get Similar Meals Algorithm Works

The algorithm starts by searching for meal records in a database, filtering the results based on certain criteria, such as the user's activity level and the time elapsed since the meal. It then goes through a series of four steps, with each step progressively relaxing the constraints on what is considered a "similar meal."

1. In the first step, the algorithm looks for meals with the same main carbohydrate source and the same mix of carbohydrate sources. The total amount of carbohydrates and the main carbohydrate source should be within 10% of the new meal's values. The difference between fasting and postprandial (after-meal) glucose levels should not exceed 15% of fasting glucose levels. If at least one such meal is found, the search stops and the top 3 results are returned.
2. If no results are found in the first step, the second step relaxes the constraint on the mix of carbohydrate sources, only requiring the main carbohydrate source to be the same. The other criteria remain the same as in the first step.
3. If no results are found in the second step, the third step further relaxes the constraints, only requiring the main carbohydrate source to be the same and the total amount of carbohydrates to be within 10% of the new meal's values. The difference between fasting and postprandial glucose levels should still not exceed 15% of fasting glucose levels.
4. If no results are found in the third step, the fourth and final step relaxes the constraints even further. In this step, the main carbohydrate source does not have to be the same. Instead, the algorithm searches for meals with a glycemic index (GI) score within 15% of the new meal's GI score. The total amount of carbohydrates must still be within 10% of the new meal's values, and the difference between fasting and postprandial glucose levels should not exceed 15% of fasting glucose levels.

If at least one meal is found in any of the steps, the search stops, and the top 3 most similar meals are returned, sorted by how close their fasting glucose levels are to the new meal's fasting glucose level. If no similar meals are found after going through all four steps, the function returns "False," indicating that no similar meals were found.

In conclusion, this code serves as a tool to help users determine their insulin dosage. By selecting similar meals, users are provided with suggestions, enabling them to make more accurate decisions for diabetes management.

## Technologies Used

- **FastAPI**: I chose FastAPI as the back-end framework for its modern, high-performance capabilities. It allowed me to create a responsive and efficient API for the application.
- **PostgreSQL**: To store and manage the application's data, I used PostgreSQL, a powerful, open-source object-relational database system.
- **YOLOv5**: I implemented the state-of-the-art, real-time object detection model YOLOv5 to identify ingredients in the user-submitted meal images.
- **Python**: I selected Python as the main programming language for developing the application because of its versatility and the rich ecosystem of libraries available.
- **HTML/CSS**: I utilized HTML and CSS to create and style the user interface of the web application.
- **Docker**: To simplify deployment and management, I leveraged Docker for containerizing the application and its dependencies, ensuring easy deployment and scaling.
- **Amazon AWS EC2**: I deployed the application on Amazon AWS EC2, a cloud-based computing platform, to guarantee scalability and reliability.
- **SQLAlchemy**: To handle interactions between the application and the PostgreSQL database, I employed SQLAlchemy, a popular SQL toolkit and Object-Relational Mapping (ORM) library for Python.

## Try App with EC2 IP

The Type 1 Diabetes Monitoring program has been deployed on an Amazon AWS EC2 instance to ensure scalability and reliability. If you would like to access the program, you can use the following IP address to access the API:

- [EC2 Instance IP: 34.207.194.103](http://34.207.194.103)

Please note that you will need to have the necessary credentials to access the instance. If you have any questions or issues accessing the program, feel free to contact me.

## Video Description

A video overview of the Type 1 Diabetes Monitoring program can be found [here](https://www.youtube.com/watch?v=35GE16QqubY).

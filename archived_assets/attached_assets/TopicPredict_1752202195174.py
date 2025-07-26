import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

# Define Cars dataset directly
data = pd.read_csv('./Rekalabs/Score.csv')
cars = pd.DataFrame(data)

# Assuming the dataset has columns: 'speed', 'doors', and 'type'
# 'type' is the target variable (categorical), and 'speed' and 'doors' are features
X_clf = cars[[
    'total_qs',
    'total_qs_addition',
    'total_qs_substraction',
    'total_qs_multipication',
    'total_answer_right_addition',
    'total_answer_right_subtraction',
    'total_answer_right_multplication'
]]
y_clf = cars['recommend']

# Split data
X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
    X_clf, y_clf, test_size=0.2, random_state=42)

# Train Logistic Regression model
clf = LogisticRegression(max_iter=200)
clf.fit(X_train_clf, y_train_clf)

# Function to predict car type based on user input
def predict_car_type():
    try:
        # Get user input for each feature used in the model
        total_qs = int(input("Enter total number of questions: "))
        total_qs_addition = int(input("Enter total number of addition questions: "))
        total_qs_substraction = int(input("Enter total number of subtraction questions: "))
        total_qs_multipication = int(input("Enter total number of multiplication questions: "))
        total_answer_right_addition = int(input("Enter total number of correct addition answers: "))
        total_answer_right_subtraction = int(input("Enter total number of correct subtraction answers: "))
        total_answer_right_multplication = int(input("Enter total number of correct multiplication answers: "))

        # Create a DataFrame for the input using the correct variable names
        input_data = pd.DataFrame({
            'total_qs': [total_qs],
            'total_qs_addition': [total_qs_addition],
            'total_qs_substraction': [total_qs_substraction],
            'total_qs_multipication': [total_qs_multipication],
            'total_answer_right_addition': [total_answer_right_addition],
            'total_answer_right_subtraction': [total_answer_right_subtraction],
            'total_answer_right_multplication': [total_answer_right_multplication]
        })

        # Predict the type using the trained model
        predicted_type = clf.predict(input_data)[0]

        print(f"The predicted subtopic type is: {predicted_type}")
    except ValueError:
        print("Invalid input. Please enter numeric values for speed and doors.")

# Call the function to test
predict_car_type()

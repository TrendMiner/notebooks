# 0) ***** Define the following variables

tm_url = "<Enter_your_TM_URL>"
model_name = "<EnterName as you want it to appear in PMML Model dropdown in tagbuilder>"
predicted_variable = "<EnterHere (e.g. Pressure, Temperature, etc.)>"
model_description = "<EnterHere>"
features = ["Enter", "Model", "Features"]
Yvalue = "Variable_To_Be_Predicted"
filename = f'{model_name}.pmml'
# MAKE SURE YOU DEFINE VIEW DATAFRAME BELOW (LINE 48)

# 1) ****** Importing needed packages

# Suggested data science package imports
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt

# TrendMiner package import
import trendminer
from trendminer.trendminer_client import TrendMinerClient
from trendminer.views import Views

# ScikitLearn packages
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

# SoftwareAG packages for converting to pmml and deployment of model
from nyoka import skl_to_pmml
from trendminer.ml.models import ZementisModels

# Create TrendMiner API object
client = TrendMinerClient("{TM_TOKEN.password}", tm_url)


# 2) ****** Loading the timeseries data from a TrendHub view

# Loading TrendHub view
# Add using the "Add TrendMiner Content" option

views = Views(client)
df = views.load_view('VIEW_UUID_HERE')
df_train=pd.concat(df)
print(df_train.head(10))


# 3) ****** Defining the features and splitting the data into training and testing set

X = df_train[features]
y = df_train[Yvalue]

# Splitting the data using the train_test_split function.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, shuffle=True)
print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)


# 4) ****** Defining the model to be used

# Creating pipeline to summarize model building "technique"
# This Pipeline function calls for a list of estimators and other operators in the form of tuples.
estimators = [('scaler', StandardScaler()),  #StandardScaler() is used to standardize the data
            ('model', LinearRegression())]
pipeline_obj = Pipeline(estimators)

# Training the model and printing the result
model1 = pipeline_obj.fit(X_train, y_train)
print(model1[1].coef_)
print(model1[1].intercept_)
print(f"y={(model1[1].coef_)[0]}*x1 + {(model1[1].coef_)[1]}*x2  +  {model1[1].intercept_}")


# 5) ****** Evaluating the model with Test Data

y_pred = model1.predict(X_test)

print("MSE = ", "{:.3f}".format(mean_squared_error(y_test, y_pred)))
print("\nCoefficient of Determination")
print("R2 =", "{:.3f}".format(r2_score(y_test, y_pred)))


# 6) ****** Converting model to PMML with Nyoka (SoftwareAG Package)

#Converting model to pmml
skl_to_pmml(pipeline=model1,
            col_names=features,
            target_name=predicted_variable,
            pmml_f_name=filename,
            model_name=model_name,
            description=model_description)


# 7) ****** Deploying the model with Zementis

#Deploying model with Zementis
with open(filename,"r") as f:
    model_string = f.read()

# But first, lets delete the model from pervious demo
zementis = ZementisModels(client)
try:
    zementis.delete_model(model_name)
except trendminer.ml.models.exceptions.MLModelNotFoundException:
    pass

# Now we can deploy the model and voila!
models = ZementisModels(client)
model_id = models.deploy_model(model_string)
model_details = models.model_details(model_id)

models = ZementisModels(client)
all_models = models.list_models()

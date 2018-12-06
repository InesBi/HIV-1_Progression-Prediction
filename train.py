# -*- coding: utf-8 -*-

"""
  This file is the training file for the final model.
  It trains the model and make predictions. 
  
  Input: trainng data from the get_features.py
  Output: model_report.txt that details the classification report of the model.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#scikit imports
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, KFold
from sklearn.metrics import classification_report, accuracy_score
#classifiers
from sklearn.linear_model import LogisticRegressionCV
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import  AdaBoostClassifier, RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import VotingClassifier
#Transformation
from sklearn.preprocessing import StandardScaler

import warnings
warnings.filterwarnings("ignore")


#Load train and test datasets
train_Data = pd.read_csv('data/training_new_data.csv')

featureSet = ["VL.t0","CD4.t0","rtlength", "pr_A", "pr_C","pr_G", 
              "pr_R", "pr_T","pr_Y", "PR_GC","RT_A", "RT_C","RT_G","RT_R", "RT_T", "RT_Y", "RT_GC"]
# featureSet = ["VL.t0":"RT_GC"]
X = train_Data[featureSet]
y = train_Data.Resp
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Data transformation with mean 0 and SD 1.
standard_scaler = StandardScaler()
X_train = standard_scaler.fit_transform(X_train)
X_test = standard_scaler.transform(X_test)

# define scoring method
scoring = 'accuracy'

# Define Top 5 models.

# TODO: Run Hyperparameters tuning on these models.
names = [" Random Forest","Neural Net", "AdaBoost","XGBoost", "Logistic Regression "]
classifiers = [
     RandomForestClassifier(bootstrap=True, max_depth=10, n_estimators=550, criterion="entropy",
                                          max_features='auto', class_weight="balanced", n_jobs=5),
     MLPClassifier(alpha=1,batch_size=30), 
     AdaBoostClassifier(),
     XGBClassifier(),
     LogisticRegressionCV(verbose=5, solver='lbfgs')
]
seed = 1
models = zip(names, classifiers)

# evaluate each model
results = []
names = []

for name, model in models:
    kfold = KFold(n_splits=10, random_state = seed)
    cv_results = cross_val_score(model, X_train, y_train, cv=kfold, scoring=scoring)
    results.append(cv_results)
    names.append(name)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    predictions = [round(value) for value in predictions]
    msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
    # Write the report to a file.
    with open('models_report.txt', 'a') as f:
        print(msg, file=f)
        print('--------------------------------------------------', file=f)
        print(accuracy_score(y_test, predictions), file=f)
        print(classification_report(y_test, predictions), file=f)
        print('--------------------------------------------------', file=f)

estimators=[(names[0], classifiers[0] ), 
            (names[1], classifiers[1]),
            (names[2], classifiers[2]),
            (names[3], classifiers[3]),
            (names[4], classifiers[4])]

# Voting based models 
votH_clf = VotingClassifier(estimators, voting='hard').fit(X_train, y_train)
predictions = votH_clf.predict(X_test)
predictions = [round(value) for value in predictions]
with open('models_report.txt', 'a') as f:
    print("Hard Voting Classifier", file=f)
    print('--------------------------------------------------', file=f)
    print(accuracy_score(y_test, predictions), file=f)
    print(classification_report(y_test, predictions), file=f)
    print('--------------------------------------------------', file=f)

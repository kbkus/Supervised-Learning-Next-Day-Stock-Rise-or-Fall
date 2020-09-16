# Supervised-Learning-Next-Day-Stock-Rise-or-Fall
## Project in progress

The goal of this project was to create a classification model that will predict if the stock price the next day will rise or fall.

API requests were made to finviz.com to pull the most recent 100 article headlines from S&P 500 companies.
The Natural Language Toolkit (NLTK) libraries were used to analyze sentiment score, which was added as a feature to the dataset.
A second set of API requests were made to Yahoo Finance to pull relavent historical stock price data for these companies.

Through feature engineering and model parameter tuning, results for next day classification are very promising.
Accuracy: 0.84
Precision: 0.85
Recall: 0.83
False Positives: 0.14
False Negatives: 0.17




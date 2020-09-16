#!/usr/bin/env python
# coding: utf-8

# In[1]:

import requests # for web scraping
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np

# sentiment analysis
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from sentiment_dictionary import NEW_WORDS

# install yahoo finance
import yfinance as yf

# In[2]:


def scrape_finviz(companies):
    """A function to scrape the finviz website.
    
    It will return the information as a data frame with columns for:
    company, date, time, headline.
    """
    
    news_tables = {} # dictionary to store the news tables from each company
    # url for the news website
    finwiz_url = 'https://finviz.com/quote.ashx?t='
    
    print('{} companies to gather data for'.format(len(companies)))
    count = 1
    
    # loop through each company you want to store data for
    for company in companies:
        print(count)
        try:
            url = finwiz_url + company
            response = requests.get(url, headers={'user-agent': 'my-app/0.0.1'})
            soup = BeautifulSoup(response.text, 'html.parser')
            # find 'news-table' in soup and load it into 'news_tables'
            news_table = soup.find(id='news-table')
            # add the table to dictionary
            news_tables[company] = news_table
            count+=1
        except:
            print('error with {}'.format(company))
            count +=1
            continue
        
    parsed_news = []
    # iterate through the news
    # iterate through the news
    for file_name, news_table in news_tables.items():
        try:
            # iterate through all tr tags in 'news_table'
            for article in news_table.find_all('tr'):
                # read the text from each tr tag into text
                # get text from a only
                text = article.a.get_text()
                # splice text in the td tag into a list
                date_scrape = article.td.text.split()
                # if the length of the 'date_scrape' is 1, load 'time' as the only element

                if len(date_scrape) == 1:
                    time = date_scrape[0]

                # else load 'date as the 1st element and 'time' as the second
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
                # extract the ticker from the file name, get the string up to the first '_'
                company = file_name.split('_')[0]

                # append ticker, date, time, and headline as a list to the parsed news list
                parsed_news.append([company, date, time, text])
        except:
            print('error with {}'.format(file_name.split('_')[0]))
            continue
            
    # convert parsed news list into a dataframe 
    columns = ['company','date','time','headline']
    parsed_news = pd.DataFrame(parsed_news, columns = columns)
    
    # delete news from Saturday and Sunday
    index_names = parsed_news[pd.to_datetime(parsed_news['date']).dt.weekday >=5].index
    parsed_news.drop(index_names, inplace = True)
    
    # reset index
    parsed_news = parsed_news.reset_index(drop=True)
    
    return parsed_news

# In[3]:
def get_stock_prices(parsed_news):
    # pull yahoo finance data to add other column values
    
    parsed_news['30d'] = ''
    parsed_news['7d'] = ''
    parsed_news['prc_30d'] = ''
    parsed_news['prc_7d'] = ''       
    parsed_news['std_30d'] = ''
    parsed_news['std_7d'] = ''
    parsed_news['open_price'] = ''
    parsed_news['high'] = ''
    parsed_news['low'] = ''
    parsed_news['close'] = ''
    parsed_news['volume'] = ''
    parsed_news['prc_volume'] = ''
    
    to_drop = []
    count = 1
    
    for i in range(len(parsed_news)):        
        if count % 300 == 0:
            parsed_news.to_csv(r'/Users/kacikus/Dropbox/Thinkful_Data_Science_Projects/Capstone2/example_save.csv')
            print('saved')
                
        if parsed_news['30d'][i] != '':
            continue
        else:
            #print(count, parsed_news['company'][i])
            try:
                # get string of company name
                ticker = parsed_news['company'][i]
                # get date range for 30 days
                # retrieving stock history automatically does not include weekends
                start_date = pd.to_datetime(parsed_news['date'][i])-timedelta(days=31)
                end_date = pd.to_datetime(parsed_news['date'][i])-timedelta(days=1)

                # object for that stock
                stock = yf.Ticker(ticker)

                # calculate changes in a month
                data = stock.history(start = start_date, end = end_date)
                # overall change in price (gross amount)
                d_month = data['Close'][-1]-data['Close'][0]
                # percentage change in price
                p_month = (data['Close'][-1]-data['Close'][0])/data['Close'][-1]
                # standard deviation
                std_month = data['Close'].std()
                # variance
                var_month = data['Close'].var()

                # get date range for 7 days
                start_date = pd.to_datetime(parsed_news['date'][i])-timedelta(days=8)
                end_date = pd.to_datetime(parsed_news['date'][i])-timedelta(days=1)
                # get data for the week
                data = stock.history(start = start_date, end = end_date)
                # overall change
                d_week = data['Close'][-1]-data['Close'][0]
                # percentage change in price
                p_week = (data['Close'][-1]-data['Close'][0])/data['Close'][-1]
                # standard deviation
                std_week = data['Close'].std()
                # variance
                var_week = data['Close'].var()

                # get the open, high, low, close, and volume traded for that day
                data = stock.history(start = pd.to_datetime(parsed_news['date'][i]))
                open_price = data['Open'][0]
                high = data['High'][0]
                low = data['Low'][0]
                close = data['Close'][0]
                volume = data['Volume'][0]

                # also want to get percent volume change from the PREVIOUS day...
                # if the date that the article came out is a Monday
                if pd.to_datetime(parsed_news['date'][i]).weekday() == 0:
                    # set the start date to Friday
                    start_date = pd.to_datetime(parsed_news['date'][i])-timedelta(days=3)
                    # set the end date to Monday
                    end_date = pd.to_datetime(parsed_news['date'][i])

                else:
                    # set the start date to the day the article came out
                    start_date = pd.to_datetime(parsed_news['date'][i])-timedelta(days=1)   
                    # set the end date to following day
                    end_date = pd.to_datetime(parsed_news['date'][i])  
                
                start_data = stock.history(start = start_date)
                end_data = stock.history(start = end_date)
                    
                #calculate how much the volume changed
                prc_volume = (end_data['Volume'][-1]-start_data['Volume'][0]) / (start_data['Volume'][0])

                # assign values to all observations that have the same ticker and date
                parsed_news['30d'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = d_month
                parsed_news['7d'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = d_week

                parsed_news['prc_30d'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = p_month
                parsed_news['prc_7d'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = p_week

                parsed_news['std_30d'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = std_month
                parsed_news['std_7d'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = std_week
                parsed_news['open_price'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = open_price
                parsed_news['high'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = high
                parsed_news['low'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = low
                parsed_news['close'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = close
                parsed_news['volume'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = volume
                parsed_news['prc_volume'].loc[(parsed_news['company']==ticker) & (parsed_news['date'] == parsed_news['date'][i])] = prc_volume
            except:
                ticker = parsed_news['company'][i]
                to_drop + list(parsed_news[parsed_news['company']==ticker].index)
                print('need to drop {}'.format(ticker))

            count+=1
    to_drop = list(dict.fromkeys(to_drop))        
    parsed_news = parsed_news.drop(to_drop)
    parsed_news = parsed_news.reset_index(drop=True)
            
    return parsed_news
            

# In[3]:

def score_sentiment(data):
    """input dataframe, loop through every headline, assign scores. Return a new dataframe.

    Data is a dataframe with company, date, time, and headline columns.
    """
    vader = SentimentIntensityAnalyzer()
    
    vader.lexicon.update(NEW_WORDS)
    
    # iterate through the headlines and get the plarity scores using vader
    scores = data['headline'].apply(vader.polarity_scores).tolist()
    # convert the 'scores' list of dicts into a dataframe
    scores_df = pd.DataFrame(scores)
    
    #join the dataframe of the news and the list of scores
    scored_data = data.join(scores_df, rsuffix='_right')
    
    # convert the date column from string to datetime
    scored_data['date'] = pd.to_datetime(data['date']).dt.date
    
    return scored_data

# In[4]:

def update_database(new_data, save = False):
    """Load .csv, append new dataframe, and save as .csv again
    
    Takes in a dataframe, data, to be appended to the master file.
    """
    # load previously saved spreadsheet
    prev_data = pd.read_csv(r'/Users/kacikus/Dropbox/Thinkful_Data_Science_Projects/Capstone2/company_data.csv', index_col = 0)
    
    # concatenate with the new data and drop duplicates
    data = pd.concat([prev_data,new_data]).drop_duplicates(subset='headline').reset_index(drop=True)

    # overwrite previous file
    if save == True:
        header = ['company', 'date', 'time', 'headline', '30d', '7d', 'prc_30d', 'prc_7d',
                  'std_30d', 'std_7d', 'open_price', 'high', 'low', 'close', 'volume',
                  'neg', 'neu', 'pos', 'compound']
        data.to_csv(r'/Users/kacikus/Dropbox/Thinkful_Data_Science_Projects/Capstone2/company_data.csv', header = header)
    
    return data

# In[5]:
def update_score(data, save = False):
    """Update the sentiment score columns including new dictionary words.
    
    Takes in a dataframe that already has been scored by 'score_sentiment' and re-calculates the
    polarity of the data including new, domain specific words
    """
    # drop old polarities
    data = data.drop(columns = ['neg', 'neu', 'pos', 'compound'], axis = 1)
    
    # initialize sentiment analyzer
    vader = SentimentIntensityAnalyzer()
    # update the dictionary
    vader.lexicon.update(NEW_WORDS)
    
    # iterate through the headlines and get the plarity scores using vader
    scores = data['headline'].apply(vader.polarity_scores).tolist()
    # convert the 'scores' list of dicts into a dataframe
    scores_df = pd.DataFrame(scores)
    
    #join the dataframe of the news and the list of scores
    scored_data = data.join(scores_df, rsuffix='_right') 
    
    # overwrite previous file
    if save == True:
        header = ['company', 'date', 'time', 'headline', '30d', '7d', 'prc_30d', 'prc_7d',
                  'std_30d', 'std_7d', 'open_price', 'high', 'low', 'close', 'volume',
                  'neg', 'neu', 'pos', 'compound']
        scored_data.to_csv(r'/Users/kacikus/Dropbox/Thinkful_Data_Science_Projects/Capstone2/company_data.csv', header = header)
    
    return scored_data
    
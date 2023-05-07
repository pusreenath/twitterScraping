#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import snscrape.modules.twitter as sntwitter
import pandas as pd
import pymongo
import urllib.parse
import json

# Define function to scrape Twitter data and store it in MongoDB
def scrape_tweets(keyword, start_date, end_date, max_tweets):
    tweets_list = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} since:{start_date} until:{end_date}').get_items()):
        if i >= max_tweets:
            break
        tweet_dict = {
            'Date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
            'ID': tweet.id,
            'URL': tweet.url,
            'Content': tweet.rawContent,
            'User': tweet.user.username,
            'Reply Count': tweet.replyCount,
            'Retweet Count': tweet.retweetCount,
            'Language': tweet.lang,
            'Source': tweet.sourceLabel,
            'Like Count': tweet.likeCount
        }
        tweets_list.append(tweet_dict)
    data_dict = {
        'Scraped Word': keyword,
        'Scraped Date': f'{start_date} - {end_date}',
        'Scraped Data': tweets_list
    }
    collection.insert_one(data_dict)

# Define function to download Twitter data as CSV
def download_csv(keyword):
    cursor = collection.find({'Scraped Word': keyword})
    tweets_list = cursor[0]['Scraped Data']
    df = pd.DataFrame(tweets_list)
    csv = df.to_csv(index=False)
    return csv

# Define function to download Twitter data as JSON
def download_json(keyword):
    cursor = collection.find({'Scraped Word': keyword})
    tweets_list = cursor[0]['Scraped Data']
    return tweets_list
# handling errors

# Set up MongoDB client and connect to database
username = "quirkyturtle"
password = "test123"

escaped_username = urllib.parse.quote_plus(username)
escaped_password = urllib.parse.quote_plus(password)

uri = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.drl3ipz.mongodb.net/twitter_data"

client = pymongo.MongoClient(uri)
db = client['twitter_data']
collection_name = 'tweets'
collection = db[collection_name]


# Set up Streamlit app
st.title('Twitter Scraper')
keyword = st.text_input('Enter keyword or hashtag:')
start_date = st.date_input('Enter start date:')
end_date = st.date_input('Enter end date:')
max_tweets = st.number_input('Enter maximum number of tweets to scrape:', min_value=1, step=1, value=100)
if st.button('Scrape data'):
    scrape_tweets(keyword, start_date, end_date, max_tweets)
    st.success('Data scraped and stored in database')
if st.button('Download CSV'):
    csv = download_csv(keyword)
    st.download_button('Download CSV', csv, 'twitter_data.csv', 'text/csv')
if st.button('Download JSON'):
    json_list = download_json(keyword)
    twitter_dict = dict()
    twitter_dict['tweet_list'] = json_list
    twitter_json = json.dumps(twitter_dict)
    st.download_button('Download JSON', twitter_json, 'twitter_data.json', 'application/json')


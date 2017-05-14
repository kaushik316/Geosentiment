from auth import consumer_secret, consumer_key, access_token, access_token_secret, plotkey
import requests
import tweepy 
import re
from textblob import TextBlob
import nltk
import plotly.plotly as py
import pandas as pd
import plotly.tools as tls
import pprint

# List of fallback searchterms in case form is submitted with an empty string
fallback_list = ["Donald Trump", "America", "Pizza"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_us_cities.csv')
pop_df = df.iloc[0:20]
pop_df.astype("str",copy=False)

# TextBlob works by taking a 'Blob' of text and converting it to a class with various methods
# This function takes a list as an input and then converts it to a blob
def get_sentiment(tweetlist):
	joined_list = " ".join(x for x in tweetlist)
	tweet_blob = TextBlob(joined_list)
	sentiment_on_search = tweet_blob.sentiment
	return sentiment_on_search[0]
	

def clean_tweets(wordlist):
	for i in range(0, len(wordlist)):
		wordlist[i] = re.sub(r'#','',wordlist[i])
		wordlist[i] = re.sub(r"RT|http\S+|@\S+","",wordlist[i])


def map_sentiment(searchterm):
	tweetlist = []
	for index, row in pop_df.iterrows():
		city_tweets = [tweet.text for tweet in tweepy.Cursor(api.search,q=searchterm,count=50,geocode="{0},{1},30mi".format(row["lat"],row["lon"])).items(50)]
		clean_tweets(city_tweets)
		sentiment = get_sentiment(city_tweets)
		tweetlist.append(sentiment)
	sent_on_tweets = pd.Series(tweetlist, name="sentiment")
	joined_df = pd.concat([pop_df,sent_on_tweets],axis=1)
	return joined_df

# Set up variables we will used in the plot and sign in to plotly
py.sign_in('kaushik.316', plotkey)
sentiment_limits = [(-0.99,-0.75),(-0.75,-0.50),(-0.50,-0.20),(-0.20, -0.01),(0.00,0.20),(0.20,0.50),(0.50,0.75),(0.75,0.99)]
sentiment_colors = ["rgba(255,65,54,0.9)","rgba(255,65,54,0.7)","rgba(255,65,54,0.5)","rgba(255,65,54,0.2)", "rgba(0,116,217,0.2)","rgba(0,116,217,0.5)","rgba(0,116,217,0.7)","rgba(0,116,217,0.9)"]
cities = []
scale = 7000

# Produces a color based on sentiment
def get_color(item):
    for i,val in enumerate(sentiment_limits):
        if val[0] < item["sentiment"].iloc[0] < val[1]:
            return sentiment_colors[i] 
    return "rgba(250,250,250,0.7)"  


# Build the plot
def build_plot(searchterm, joined_df, chart_title):
	joined_df['text'] = joined_df['name'] + '<br>Population ' + (joined_df['pop']/1e6).astype(str)+' million'

	for i in range(len(joined_df)):
	    pop_df_sub = joined_df.iloc[[i]]
	    marker_color = get_color(pop_df_sub)
	    city = dict(
	        type = 'scattergeo',
	        locationmode = 'USA-states',
	        lon = pop_df_sub['lon'],
	        lat = pop_df_sub['lat'],
	        text = pop_df_sub['text'] + '</br>' + "Sentiment polarity: %.2f " % (float(pop_df_sub['sentiment'])),
	        marker = dict(
	            size = pop_df_sub['pop']/scale,
	            color = marker_color,
	            line = dict(width=0.5, color='rgb(40,40,40)'),
	            sizemode = 'area'
	        ),
	        name = '' )
	    cities.append(city)

	layout = dict(
	        title = 'US city sentiment on "{}"'.format(chart_title),
	        showlegend = False,
	        geo = dict(
	            scope='usa',
	            projection=dict( type='albers usa' ),
	            showland = True,
	            landcolor = 'rgb(217, 217, 217)',
	            subunitwidth=1,
	            countrywidth=1,
	            subunitcolor="rgb(255, 255, 255)",
	            countrycolor="rgb(255, 255, 255)"
	        ),
	    )

	fig = dict( data=cities, layout=layout )
	py.plot( fig, validate=False, filename='d3-bubble-map-populations' )



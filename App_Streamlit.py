"""
Update on Thu Agust 05 17:42:01 2021

@author: Adi syahadi
"""



import streamlit as st
import warnings
warnings.filterwarnings("ignore")
# EDA Pkgs
import pandas as pd
import numpy as np
import pandas as pd
import tweepy
import json
from tweepy import OAuthHandler
import re
import textblob
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import openpyxl
import time
import tqdm

#To Hide Warnings
st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)
# Viz Pkgs
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
#sns.set_style('darkgrid')


STYLE = """
<style>
img {
    max-width: 100%;
}
</style> """

def main():
    """ Penjelajah Kumpulan Data ML Umum """
    #st.title("Live twitter Sentiment analysis")
    #st.subheader("Pilih topik yang ingin Anda analisis sentimennya")

    html_temp = """
	<div style="background-color:tomato;"><p style="color:white;font-size:40px;padding:9px">Live twitter Sentiment analysis</p></div>
	"""
    st.markdown(html_temp, unsafe_allow_html=True)
    st.subheader("Pilih topik yang ingin Anda analisis sentimennya :")

    ################# Twitter API Connection #######################
    consumer_key = "Enter Key Here"
    consumer_secret = "Enter Key Here"
    access_token = "Enter Key Here"
    access_token_secret = "Enter Key Here"



    # Use the above credentials to authenticate the API.

    auth = tweepy.OAuthHandler( consumer_key , consumer_secret )
    auth.set_access_token( access_token , access_token_secret )
    api = tweepy.API(auth)
    ################################################################
    
    df = pd.DataFrame(columns=["Date","User","IsVerified","Tweet","Likes","RT",'User_location'])
    
    # Write a Function to extract tweets:
    def get_tweets(Topic,Count):
        i=0
        #my_bar = st.progress(100) # To track progress of Extracted tweets
        for tweet in tweepy.Cursor(api.search, q=Topic,count=100, lang="en",exclude='retweets').items():
            #time.sleep(0.1)
            #my_bar.progress(i)
            df.loc[i,"Date"] = tweet.created_at
            df.loc[i,"User"] = tweet.user.name
            df.loc[i,"IsVerified"] = tweet.user.verified
            df.loc[i,"Tweet"] = tweet.text
            df.loc[i,"Likes"] = tweet.favorite_count
            df.loc[i,"RT"] = tweet.retweet_count
            df.loc[i,"User_location"] = tweet.user.location
            #df.to_csv("TweetDataset.csv",index=False)
            #df.to_excel('{}.xlsx'.format("TweetDataset"),index=False)   ## Save as Excel
            i=i+1
            if i>Count:
                break
            else:
                pass
    # Function to Clean the Tweet.
    def clean_tweet(tweet):
        return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|([RT])', ' ', tweet.lower()).split())
    
        
    # Funciton to analyze Sentiment
    def analyze_sentiment(tweet):
        analysis = TextBlob(tweet)
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'
    
    #Function to Pre-process data for Worlcloud
    def prepCloud(Topic_text,Topic):
        Topic = str(Topic).lower()
        Topic=' '.join(re.sub('([^0-9A-Za-z \t])', ' ', Topic).split())
        Topic = re.split("\s+",str(Topic))
        stopwords = set(STOPWORDS)
        stopwords.update(Topic) ### Add our topic in Stopwords, so it doesnt appear in wordClous
        ###
        text_new = " ".join([txt for txt in Topic_text.split() if txt not in stopwords])
        return text_new

    
    #
    from PIL import Image
    image = Image.open('Logo1.jpg')
    st.image(image, caption='Twitter for Analytics',use_column_width=True)
    
    
    # Collect Input from user :
    Topic = str()
    Topic = str(st.text_input("Enter the topic you are interested in (Press Enter once done)"))     
    
    if len(Topic) > 0 :
        
        # Call the function to extract the data. pass the topic and filename you want the data to be stored in.
        with st.spinner("Please wait, Tweets are being extracted"):
            get_tweets(Topic , Count=200)
        st.success('Tweets have been Extracted !!!!')    
           
    
        # Call function to get Clean tweets
        df['clean_tweet'] = df['Tweet'].apply(lambda x : clean_tweet(x))
    
        # Call function to get the Sentiments
        df["Sentiment"] = df["Tweet"].apply(lambda x : analyze_sentiment(x))
        
        
        # Write Summary of the Tweets
        st.write("Total Tweet yang Diekstrak untuk Topik '{}' are : {}".format(Topic,len(df.Tweet)))
        st.write("Total Tweet Positif adalah : {}".format(len(df[df["Sentiment"]=="Positive"])))
        st.write("Total Tweet Negatif adalah : {}".format(len(df[df["Sentiment"]=="Negative"])))
        st.write("Total Tweet Netral adalah : {}".format(len(df[df["Sentiment"]=="Neutral"])))
        
        # See the Extracted Data : 
        if st.button("Lihat Data yang Diekstrak"):
            #st.markdown(html_temp, unsafe_allow_html=True)
            st.success("Di bawah ini adalah Data yang Diekstrak :")
            st.write(df.head(50))
        
        
        # get the countPlot
        if st.button("Dapatkan Count Plot untuk Sentimen Berbeda"):
            st.success("Menghasilkan Plot Hitungan")
            st.subheader("Hitung Plot untuk Sentimen yang Berbeda")
            st.write(sns.countplot(df["Sentiment"]))
            st.pyplot()
        
        # Piechart 
        if st.button("Dapatkan Diagram Lingkaran untuk Sentimen yang Berbeda"):
            st.success("Membuat Bagan Pai")
            a=len(df[df["Sentiment"]=="Positive"])
            b=len(df[df["Sentiment"]=="Negative"])
            c=len(df[df["Sentiment"]=="Neutral"])
            d=np.array([a,b,c])
            explode = (0.1, 0.0, 0.1)
            st.write(plt.pie(d,shadow=True,explode=explode,labels=["Positive","Negative","Neutral"],autopct='%1.2f%%'))
            st.pyplot()
            
            
        # get the countPlot Based on Verified and unverified Users
        if st.button("Dapatkan Plot Hitungan Berdasarkan Pengguna Terverifikasi dan Tidak Terverifikasi"):
            st.success("Menghasilkan Plot Hitungan (Pengguna Terverifikasi dan Tidak Terverifikasi)")
            st.subheader("Hitung Plot untuk Sentimen Berbeda untuk Pengguna yang Terverifikasi dan yang belum terverifikasi")
            st.write(sns.countplot(df["Sentiment"],hue=df.IsVerified))
            st.pyplot()
        
        
        ## Points to add 1. Make Backgroud Clear for Wordcloud 2. Remove keywords from Wordcloud
        
        
        # Create a Worlcloud
        if st.button("Dapatkan WordCloud untuk semua hal yang dikatakan tentang {}".format(Topic)):
            st.success("Menghasilkan WordCloud untuk semua hal yang dikatakan tentang {}".format(Topic))
            text = " ".join(review for review in df.clean_tweet)
            stopwords = set(STOPWORDS)
            text_newALL = prepCloud(text,Topic)
            wordcloud = WordCloud(stopwords=stopwords,max_words=800,max_font_size=70).generate(text_newALL)
            st.write(plt.imshow(wordcloud, interpolation='bilinear'))
            st.pyplot()
        
        
        #Wordcloud for Positive tweets only
        if st.button("Dapatkan WordCloud untuk semua Tweet Positif tentang {}".format(Topic)):
            st.success("Menghasilkan WordCloud untuk semua Tweet Positif tentang {}".format(Topic))
            text_positive = " ".join(review for review in df[df["Sentiment"]=="Positive"].clean_tweet)
            stopwords = set(STOPWORDS)
            text_new_positive = prepCloud(text_positive,Topic)
            #text_positive=" ".join([word for word in text_positive.split() if word not in stopwords])
            wordcloud = WordCloud(stopwords=stopwords,max_words=800,max_font_size=70).generate(text_new_positive)
            st.write(plt.imshow(wordcloud, interpolation='bilinear'))
            st.pyplot()
        
        
        #Wordcloud for Negative tweets only       
        if st.button("Dapatkan WordCloud untuk semua Tweet Negatif tentang {}".format(Topic)):
            st.success("Menghasilkan WordCloud untuk semua Tweet Positif tentang {}".format(Topic))
            text_negative = " ".join(review for review in df[df["Sentiment"]=="Negative"].clean_tweet)
            stopwords = set(STOPWORDS)
            text_new_negative = prepCloud(text_negative,Topic)
            #text_negative=" ".join([word for word in text_negative.split() if word not in stopwords])
            wordcloud = WordCloud(stopwords=stopwords,max_words=800,max_font_size=70).generate(text_new_negative)
            st.write(plt.imshow(wordcloud, interpolation='bilinear'))
            st.pyplot()
        
        
        
        
        
    st.sidebar.header("About App")
    st.sidebar.info("Proyek analisis Sentimen Twitter yang akan menghapus twitter untuk topik yang dipilih oleh pengguna. Tweet yang diekstraksi kemudian akan digunakan untuk menentukan Sentimen dari tweet tersebut. \
                    Visualisasi yang berbeda akan membantu kami merasakan suasana hati orang-orang di Twitter secara keseluruhan terkait topik yang kami pilih.")
    st.sidebar.text("Dibangun dengan Streamlit")
    
    st.sidebar.header("Untuk Setiap Pertanyaan/Saran Silakan hubungi di :")
    st.sidebar.info("adisyahadi41@gmail.com")
    #st.sidebar.subheader("Scatter-plot setup")
    #box1 = st.sidebar.selectbox(label= "X axis", options = numeric_columns)
    #box2 = st.sidebar.selectbox(label="Y axis", options=numeric_columns)
    #sns.jointplot(x=box1, y= box2, data=df, kind = "reg", color= "red")
    #st.pyplot()



    if st.button("Exit"):
        st.balloons()



if __name__ == '__main__':
    main()


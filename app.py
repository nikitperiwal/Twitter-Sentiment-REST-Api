from gettweets import get_tweets
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from classifier import predict_sentiment


# Initiate app instance
app = FastAPI(title='Twitter Sentiment API',
              version='1.0',
              description='A REST API to extract tweets, and run sentiment analysis on it.')


# Design the incoming feature data
class SearchData(BaseModel):
    keywords: str
    exclude_words: float
    start_date: str
    end_date: str
    num_tweets: int


# Api root or home endpoint
@app.get('/')
def getTweet(keywords: str,
             exclude_words: str,
             start_date: str,
             end_date: str,
             num_tweets: int):
    """
    This endpoint serves the predictions based on the values received from a user and the saved model.

    Parameters:
    -----------
    keywords     : str
        strings of words to search for.
    exclude_words : str
        strings of words that shouldn't be included in results.
    start_date   : datetime
        Date from which tweets are to be scraped
    end_date     : datetime
        Date until which tweets are to scraped
    num_tweets : int
        Number of tweets to scrap daily.
    """

    df = get_tweets(keywords,
                    exclude_words,
                    start_date,
                    end_date,
                    num_tweets)

    df['processed_text'], df['sentiment'] = predict_sentiment(list(df['text']))
    df['sentiment'] = df['sentiment'].map({1: 'positive', -1: 'negative'})

    tweets = []
    for i, row in df.iterrows():
        tweets.append(dict(datetime=row['datetime'], tweet_url=row['tweet_url'], username=row['username'],
                           text=row['text'], char_length=row['char_length'], word_length=row['word_length'],
                           likes=row['likes'], retweets=row['retweets'], processed_text=row['processed_text'],
                           sentiment=row['sentiment']))

    return {'tweets': tweets}


if __name__ == "__main__":
    # Run app with uvicorn with port and host specified. Host needed for docker port mapping.
    uvicorn.run(app, port=8000, host="127.0.0.1")

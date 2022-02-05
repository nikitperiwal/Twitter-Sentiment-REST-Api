import pandas as pd
import datetime as dt
import tweepy
from concurrent.futures.thread import ThreadPoolExecutor


def request(api, search_string, start_date, end_date, tweet_no):
    """
    Request for tweets using 'GetOldTweets3' module.

    Parameters:
    -----------
    search    : str
        String to search for in tweets.
    start_date: datetime
        Date from which tweets are to be scraped
    end_date  : datetime
        Date until which tweets are to scraped
    tweetno   : int
        Number of tweets to scrap from the given time period
    """

    tweets = api.search_tweets(
        q=search_string,
        lang="en",
        #since=str(start_date),
        until=str(end_date),
        result_type="popular",
        tweet_mode="extended",
        count=tweet_no,
    )

    data = list()
    for tweet in tweets:
        data.append((
            tweet.created_at,
            "https://twitter.com/twitter/statuses/" + str(tweet.id),
            tweet.user.screen_name,
            tweet.full_text.replace('\n', ''),
            len(tweet.full_text),
            len(tweet.full_text.split()),
            tweet.favorite_count,
            tweet.retweet_count
        ))
    return data


def get_tweets(keywords, exclude_words=(), start_date='', end_date='', num_tweets=100):
    """
    Get Tweets for passed keywords from given time period.
    Increases the speed of scraping by using threads.

    Parameters:
    -----------
    keywords     : str
        strings of words to search for.
    excludewords : str
        strings of words that shouldn't be included in results.
    start_date   : datetime
        Date from which tweets are to be scraped
    end_date     : datetime
        Date until which tweets are to scraped
    num_tweets : int
        Number of tweets to scrap daily.
    """

    # Checking variable data
    assert any(keywords), "Please include a word to search for in keywords."
    assert start_date != '', "Please enter the start date."
    assert end_date != '', "Please enter the end date."

    # Converting variable type
    if isinstance(start_date, str):
        s_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        start_date = s_date.date()

    if isinstance(end_date, str):
        e_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
        end_date = e_date.date()

    if isinstance(num_tweets, str):
        num_tweets = int(num_tweets)

    search = keywords.replace(", ", " OR ")
    for word in exclude_words.split(', '):
        search += ' -' + word

    day = dt.timedelta(1)

    consumer_token = 'jgZOWpaf9GBwh6Jm4mBGfuYf3'
    consumer_secret = 'XBusV3FDNOgoIwwuSj1upo59wAMJtX8tTT3lJCsFDvKx7cKbIr'
    access_token = '835280725859524609-TRGPJ93ex0k6kkqTJ9HsAjSJM2d5F2P'
    access_token_secret = 'gfRumhidMK3aAJ8WE5haWNFtjC03n61BEYcHJidC7DNCn'

    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Using Threading to improve speed.
    futurelist = list()
    with ThreadPoolExecutor(max_workers=7) as executor:
        while start_date <= end_date:
            futurelist.append(executor.submit(request, api, search, start_date, start_date + day, num_tweets))
            start_date += day

    # Collecting the data from the threads
    data = list()
    for x in futurelist:
        data.extend(x.result())

    # Create a pandas dataframe to store the tweets.
    columns = ['datetime', 'tweet_url', 'username', 'text', 'char_length', 'word_length', 'likes', 'retweets']
    df = pd.DataFrame(data, columns=columns)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df


if __name__ == "__main__":
    dframe = get_tweets(keywords='Trump', exclude_words='',
                        start_date='2022-01-23', end_date='2022-01-30',
                        num_tweets=10)
    print(dframe.head)

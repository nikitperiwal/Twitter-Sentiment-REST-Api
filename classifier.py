import re
import pickle
import numpy as np
import pandas as pd
from tensorflow.keras import backend
from tensorflow.keras import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Bidirectional, GlobalMaxPool1D, Dense, LSTM, Conv1D, Embedding

# Reading contractions.csv and storing it as a dict.
contractions = pd.read_csv('models/contractions.csv', index_col='Contraction')
contractions.index = contractions.index.str.lower()
contractions.Meaning = contractions.Meaning.str.lower()
contractions_dict = contractions.to_dict()['Meaning']

# Defining regex patterns.
urlPattern = r"((http://)[^ ]*|(https://)[^ ]*|(www\.)[^ ]*)"
userPattern = r'@[^\s]+'
hashtagPattern = r'#[^\s]+'
alphaPattern = r"[^a-z0-9<>]"
sequencePattern = r"(.)\1\1+"
seqReplacePattern = r"\1\1"

# Defining regex for emojis
emoji_smile = r"[8:=;]['`\-]?[)d]+"
emoji_sad = r"[8:=;]['`\-]?\(+"
emoji_neutral = r"[8:=;]['`\-]?[\/|l*]"
emoji_lol = r"[8:=;]['`\-]?p+"


def preprocess_apply(tweet):
    """
    Preprocesses the passed Tweet by replacing emojis, urls, etc.

    Parameters:
    -----------
    tweet    : str
        Tweet to preprocess, as a String.
    """

    tweet = tweet.lower()
    # Replace all URls with '<url>'
    tweet = re.sub(urlPattern, '<url>', tweet)
    # Replace @USERNAME to '<user>'.
    tweet = re.sub(userPattern, '<user>', tweet)
    # Replace #Hashtags to '<hashtags>'.
    tweet = re.sub(userPattern, '<hashtag>', tweet)
    # Replace 3 or more consecutive letters by 2 letter.
    tweet = re.sub(sequencePattern, seqReplacePattern, tweet)
    # Replace all emojis.
    tweet = re.sub(r'<3', '<heart>', tweet)
    tweet = re.sub(emoji_smile, '<smile>', tweet)
    tweet = re.sub(emoji_sad, '<sadface>', tweet)
    tweet = re.sub(emoji_neutral, '<neutralface>', tweet)
    tweet = re.sub(emoji_lol, '<lolface>', tweet)
    for contraction, replacement in contractions_dict.items():
        tweet = tweet.replace(contraction, replacement)
    # Remove non-alphanumeric and symbols
    tweet = re.sub(alphaPattern, ' ', tweet)
    # Adding space on either side of '/' to separate words (After replacing URLS).
    tweet = re.sub(r'/', ' / ', tweet)
    return tweet


def load_model():
    """
    Creates the sentiment model.
    Returns the model after loading the weights.
    """

    embedding_layer = Embedding(input_dim=60000,
                                output_dim=100,
                                input_length=60)

    model = Sequential([
        embedding_layer,
        Bidirectional(LSTM(100, dropout=0.3, return_sequences=True)),
        Bidirectional(LSTM(100, dropout=0.3, return_sequences=True)),
        Conv1D(100, 5, activation='relu'),
        GlobalMaxPool1D(),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid'),
    ], name="Sentiment_Model")

    model.load_weights("models/weights")
    return model


def predict_sentiment(text):
    """
    Predicts sentiment on the passed list of texts.
    The list of text is preprocessed, tokenized and then predicted on.

    Parameters:
    -----------
    text    : list
        List of tweet to predict on.
    """

    if isinstance(text, str):
        text = list(text, )
    processed_text = [preprocess_apply(t) for t in text]
    text = pad_sequences(tokenizer.texts_to_sequences(processed_text), maxlen=60)
    sentiment = sentiment_model.predict(text)
    sentiment = np.where(sentiment > 0.5, 1, -1)
    return processed_text, sentiment


backend.clear_session()
with open('models/Tokenizer.pickle', 'rb') as file:
    tokenizer = pickle.load(file)
sentiment_model = load_model()
sentiment_model.summary()

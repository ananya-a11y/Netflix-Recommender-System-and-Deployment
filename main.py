import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import bs4 as bs
import urllib.request
import pickle
import requests

app = Flask(__name__)

# Load ML model and vectorizer
try:
    clf = pickle.load(open('nlp_model.pkl', 'rb'))
    vectorizer = pickle.load(open('transform.pkl','rb'))  # fixed typo: tranform -> transform
except Exception as e:
    raise Exception("Model loading failed. Ensure 'nlp_model.pkl' and 'transform.pkl' are present.", e)

# Load movie data and create similarity matrix
def create_similarity():
    data = pd.read_csv('main_data.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    similarity = cosine_similarity(count_matrix)
    return data, similarity

# Movie recommender function
def rcmd(movie):
    movie = movie.lower()
    try:
        data, similarity = create_similarity()
    except Exception as e:
        return f"Error in recommendation system: {e}"

    if movie not in data['movie_title'].str.lower().values:
        return 'Sorry! Try another movie name.'

    i = data.loc[data['movie_title'].str.lower() == movie].index[0]
    lst = list(enumerate(similarity[i]))
    lst = sorted(lst, key=lambda x: x[1], reverse=True)[1:11]
    return [data['movie_title'][i[0]] for i in lst]

# Convert stringified list to actual list
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["', '')
    my_list[-1] = my_list[-1].replace('"]', '')
    return my_list

# Get movie suggestions for autocomplete
def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

@app.route("/")
@app.route("/home")
def home():
    suggestions = get_suggestions()
    app.run(debug=True)

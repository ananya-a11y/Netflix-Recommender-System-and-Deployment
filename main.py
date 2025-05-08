import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import logging

app = Flask(__name__, template_folder='.')  

# Global variables
clf = None
vectorizer = None
data = None
suggestions_list = None

def load_model_and_vectorizer():
    global clf, vectorizer
    if clf is None or vectorizer is None:
        try:
            clf = pickle.load(open('nlp_model.pkl', 'rb'))
            vectorizer = pickle.load(open('transform.pkl', 'rb'))
            logging.info("Model and vectorizer loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model or vectorizer: {e}")
            raise

def load_data(reduce_data=False, num_samples=3000):
    global data, suggestions_list
    if data is None:
        try:
            data = pd.read_csv('main_data.csv')
            if reduce_data:
                if len(data) > num_samples:
                    data = data.sample(n=num_samples, random_state=42)
                    logging.info(f"Data reduced to {num_samples} samples using random sampling.")
                else:
                    logging.warning(f"Data already <= {num_samples}, no reduction needed.")
            suggestions_list = list(data['movie_title'].str.capitalize())
            logging.info("Data loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise

def get_suggestions():
    global suggestions_list
    if suggestions_list is None:
        load_data()
    return suggestions_list if suggestions_list is not None else []

def rcmd(movie):
    global data, vectorizer
    if data is None:
        load_data()
    if vectorizer is None:
        load_model_and_vectorizer()
    if data is None or vectorizer is None:
        return "Error: Data or model is not available."

    movie = movie.lower()
    if movie not in data['movie_title'].str.lower().values:
        return 'Sorry! Try another movie name.'
    try:
        movie_index = data.loc[data['movie_title'].str.lower() == movie].index[0]
        movie_comb = data['comb'].iloc[movie_index]
        movie_vector = vectorizer.transform([movie_comb])
        similarity_scores = cosine_similarity(movie_vector, vectorizer.transform(data['comb']))[0]
        similar_movies = sorted(list(enumerate(similarity_scores)), key=lambda x: x[1], reverse=True)[1:11]
        return [data['movie_title'][i[0]] for i in similar_movies]
    except Exception as e:
        logging.error(f"Error calculating similarity: {e}")
        return "Error calculating movie recommendations."

@app.route('/', methods=['GET', 'HEAD'])
@app.route('/home', methods=['GET', 'HEAD'])
def home():
    try:
        suggestions = get_suggestions()
        return render_template('home.html', suggestions=suggestions)
    except Exception as e:
        logging.error(f"Error rendering home.html: {e}")
        return f"Error rendering home.html: {e}", 500

@app.route("/similarity", methods=["POST"])
def get_similarity():
    movie = request.form.get('name')
    if not movie:
        return jsonify({"error": "No movie name provided."})
    try:
        recs = rcmd(movie)
        if isinstance(recs, str):
            return jsonify({"error": recs})
        return jsonify({"recommendations": recs})
    except Exception as e:
        logging.error(f"Error in /similarity: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        details = {key: request.form[key] for key in request.form}
        suggestions = get_suggestions()
        for k in ['rec_movies', 'rec_posters', 'cast_names', 'cast_chars', 'cast_profiles', 'cast_bdays', 'cast_bios', 'cast_places']:
            if k in details:
                details[k] = details[k].split('","')
                details[k][0] = details[k][0].replace('["', '')
                details[k][-1] = details[k][-1].replace('"]', '')
        cast_ids = details['cast_ids'].strip('[]').split(',')
        movie_cards = {details['rec_posters'][i]: details['rec_movies'][i] for i in range(len(details['rec_movies']))}
        casts = {details['cast_names'][i]: [cast_ids[i], details['cast_chars'][i], details['cast_profiles'][i]] for i in range(len(details['cast_names']))}
        cast_details = {details['cast_names'][i]: [cast_ids[i], details['cast_profiles'][i], details['cast_bdays'][i], details['cast_places'][i], details['cast_bios'][i]] for i in range(len(details['cast_names']))}
        movie_reviews = {}
        return render_template('recommend.html',
                                        title=details['title'],
                                        poster=details['poster'],
                                        overview=details['overview'],
                                        vote_average=details['rating'],
                                        vote_count=details['vote_count'],
                                        release_date=details['release_date'],
                                        runtime=details['runtime'],
                                        status=details['status'],
                                        genres=details['genres'],
                                        movie_cards=movie_cards,
                                        reviews=movie_reviews,
                                        casts=casts,
                                        cast_details=cast_details,
                                        suggestions=suggestions)
    except Exception as e:
        logging.error(f"Error in /recommend: {e}")
        return f"Error in /recommend: {e}", 500

#  Add this route to provide movie titles for autocomplete
@app.route('/api/movies')
def get_movies():
    try:
        df = pd.read_csv("data1.csv")  # Or "new_data.csv", depending on which file you want to use
        movie_titles = df['movie_title'].tolist()
        return jsonify({"movies": movie_titles})
    except Exception as e:
        print(f"Error reading CSV: {e}")  # Log the error
        return jsonify({"error": "Failed to load movie data"}), 500

# Preload data for Render
load_data(reduce_data=True, num_samples=3000)
load_model_and_vectorizer()

# Expose app to gunicorn
application = app

# Run locally
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)







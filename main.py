import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import logging
from  scipy.sparse import csr_matrix

# Set up logging
logging.basicConfig(level=logging.ERROR)  # Configure logging to capture errors

app = Flask(__name__, template_folder='templates')

# Global variables for model and data (loaded on demand)
clf = None
vectorizer = None
data = None
similarity = None
suggestions_list = None # to store suggestions

def load_model_and_vectorizer():
    """Loads the ML model and vectorizer."""
    global clf, vectorizer
    if clf is None or vectorizer is None:
        try:
            clf = pickle.load(open('nlp_model.pkl', 'rb'))
            vectorizer = pickle.load(open('transform.pkl', 'rb'))
            logging.info("Model and vectorizer loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model or vectorizer: {e}")
            raise  # Re-raise the exception to be caught by the caller

def load_data_and_compute_similarity():
    """Loads the data and computes the cosine similarity matrix."""
    global data, similarity, suggestions_list
    if data is None or similarity is None:
        try:
            data = pd.read_csv('main_data.csv')
            cv = CountVectorizer()
            count_matrix = cv.fit_transform(data['comb'])
            similarity = cosine_similarity(count_matrix)
            similarity = csr_matrix(similarity)  # store similarity matrix as sparse
            suggestions_list = list(data['movie_title'].str.capitalize()) # pre-compute suggestions
            logging.info("Data loaded and similarity matrix computed.")
        except Exception as e:
            logging.error(f"Error loading data or computing similarity: {e}")
            raise  # Re-raise the exception to be caught by the caller

def get_suggestions():
    """Returns a list of movie titles.  Handles the case where data might be None."""
    global suggestions_list
    if suggestions_list is None:
        load_data_and_compute_similarity() # load data if not loaded
    return suggestions_list if suggestions_list is not None else []

def rcmd(movie):
    """Recommends movies similar to the given movie."""
    global data, similarity
    if data is None or similarity is None:
        load_data_and_compute_similarity() # load data if not loaded
    if data is None or similarity is None:
        return "Error: Data or similarity matrix is not available."

    movie = movie.lower()
    if movie not in data['movie_title'].str.lower().values:
        return 'Sorry! Try another movie name.'
    i = data.loc[data['movie_title'].str.lower() == movie].index[0]
    lst = sorted(list(enumerate(similarity[i].toarray()[0])), key=lambda x: x[1], reverse=True)[1:11] # added .toarray()
    return [data['movie_title'][i[0]] for i in lst]

@app.route('/', methods=['GET', 'HEAD'])
@app.route('/home', methods=['GET', 'HEAD'])
def home():
    """Renders the home page."""
    try:
        suggestions = get_suggestions()
        return render_template('home.html', suggestions=suggestions)
    except Exception as e:
        logging.error(f"Error rendering home.html: {e}")
        return f"Error rendering home.html: {e}", 500

@app.route("/similarity", methods=["POST"])
def get_similarity():
    """Returns movie recommendations based on similarity."""
    movie = request.form.get('name')
    if not movie:
        return jsonify({"error": "No movie name provided."})
    try:
        recs = rcmd(movie)
        if isinstance(recs, str):
            return jsonify({"error": recs})  # Return the error message from rcmd
        return jsonify({"recommendations": recs})
    except Exception as e:
        logging.error(f"Error in /similarity: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    """Renders the recommendation page with movie details."""
    try:
        details = {key: request.form[key] for key in request.form}
        suggestions = get_suggestions() # loads data if not already loaded

        for k in ['rec_movies', 'rec_posters', 'cast_names', 'cast_chars', 'cast_profiles', 'cast_bdays', 'cast_bios', 'cast_places']:
            if k in details:
                details[k] = details[k].split('","')
                details[k][0] = details[k][0].replace('["', '')  # corrected this
                details[k][-1] = details[k][-1].replace('"]', '') # corrected this

        cast_ids = details['cast_ids'].strip('[]').split(',') # corrected this
        movie_cards = {details['rec_posters'][i]: details['rec_movies'][i] for i in range(len(details['rec_movies']))}
        casts = {details['cast_names'][i]: [cast_ids[i], details['cast_chars'][i], details['cast_profiles'][i]] for i in range(len(details['cast_names']))}
        cast_details = {details['cast_names'][i]: [cast_ids[i], details['cast_profiles'][i], details['cast_bdays'][i], details['cast_places'][i], details['cast_bios'][i]] for i in range(len(details['cast_names']))}
        movie_reviews = {}
        # skipping IMDB scraping in this simplified version

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)



import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)  # Configure logging to capture errors

app = Flask(__name__, template_folder='templates')

# Load ML model and vectorizer
clf = None
vectorizer = None
try:
    clf = pickle.load(open('nlp_model.pkl', 'rb'))
    vectorizer = pickle.load(open('transform.pkl', 'rb'))
    logging.info("Model and vectorizer loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or vectorizer: {e}")
    # Consider raising an exception here if the app cannot function without the model
    # raise  # Uncomment this to halt app startup on model load failure
    #Or set default
    clf, vectorizer = None, None

# Load data and compute similarity ONCE
data = None
similarity = None
try:
    data = pd.read_csv('main_data.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    similarity = cosine_similarity(count_matrix)
    logging.info("Data loaded and similarity matrix computed.")
except Exception as e:
    logging.error(f"Error loading data or computing similarity: {e}")
    #  raise #  Uncomment this to halt app startup on data load failure
    data, similarity = None, None #set to None

def get_suggestions():
    """Returns a list of movie titles.  Handles the case where data might be None."""
    if data is not None:
        try:
            return list(data['movie_title'].str.capitalize())
        except KeyError as e:
            logging.error(f"Error accessing 'movie_title' column: {e}")
            return []
    else:
        logging.warning("Data is not loaded. Returning empty suggestions.")
        return []

def rcmd(movie):
    """Recommends movies similar to the given movie."""
    if data is None or similarity is None:
        return "Error: Data or similarity matrix is not available."

    movie = movie.lower()
    if movie not in data['movie_title'].str.lower().values:
        return 'Sorry! Try another movie name.'
    i = data.loc[data['movie_title'].str.lower() == movie].index[0]
    lst = sorted(list(enumerate(similarity[i])), key=lambda x: x[1], reverse=True)[1:11]
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
    recs = rcmd(movie)
    if isinstance(recs, str):
        return jsonify({"error": recs})  # Return the error message from rcmd
    return jsonify({"recommendations": recs})

@app.route("/recommend", methods=["POST"])
def recommend():
    """Renders the recommendation page with movie details."""
    try:
        details = {key: request.form[key] for key in request.form}
        suggestions = get_suggestions()

        for k in ['rec_movies', 'rec_posters', 'cast_names', 'cast_chars', 'cast_profiles', 'cast_bdays', 'cast_bios', 'cast_places']:
            if k in details:
                details[k] = details[k].split('","')
                details[k][0] = details[k][0].replace('["', '')  #corrected this
                details[k][-1] = details[k][-1].replace('"]', '') #corrected this

        cast_ids = details['cast_ids'].strip('[]').split(',') #corrected this
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
    ```


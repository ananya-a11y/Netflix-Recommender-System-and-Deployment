import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

app = Flask(__name__, template_folder='.')

# Load ML model and vectorizer
try:
    clf = pickle.load(open('nlp_model.pkl', 'rb'))
    vectorizer = pickle.load(open('transform.pkl','rb'))
except Exception as e:
    print(f"Model loading error: {e}")
    clf, vectorizer = None, None

def create_similarity():
    data = pd.read_csv('main_data.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    similarity = cosine_similarity(count_matrix)
    return data, similarity

data = None
similarity_matrix = None

def rcmd(movie):
    global data, similarity_matrix
    movie = movie.lower()
    if data is None or similarity_matrix is None:
        data, similarity_matrix = create_similarity()
    if movie not in data['movie_title'].str.lower().values:
        return 'Sorry! Try another movie name.'
    i = data.loc[data['movie_title'].str.lower() == movie].index[0]
    lst = list(enumerate(similarity_matrix[i]))
    lst = sorted(lst, key=lambda x: x[1], reverse=True)[1:11]
    return [data['movie_title'][i[0]] for i in lst]

@app.route('/', methods=['GET', 'HEAD'])
@app.route('/home', methods=['GET', 'HEAD'])
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return f"Error rendering home.html: {e}", 500

@app.route("/similarity", methods=["POST"])
def get_similarity():
    movie = request.form.get('name')
    if not movie:
        return "No movie name provided.", 400
    recs = rcmd(movie)
    if isinstance(recs, str):
        return recs
    return jsonify({"recommendations": recs})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

    



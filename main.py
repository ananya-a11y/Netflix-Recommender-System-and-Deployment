import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set Streamlit page configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Load ML model and vectorizer
@st.cache_resource
def load_model():
    try:
        clf = pickle.load(open('nlp_model.pkl', 'rb'))
        vectorizer = pickle.load(open('transform.pkl','rb'))
        return clf, vectorizer
    except Exception as e:
        st.error(f"Model loading error: {e}")
        return None, None

# Load data and compute similarity
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('main_data.csv')
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(data['comb'])
        similarity = cosine_similarity(count_matrix)
        return data, similarity
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None, None

clf, vectorizer = load_model()
data, similarity = load_data()

# Function to return recommendations
def get_recommendations(movie):
    movie = movie.lower()
    if movie not in data['movie_title'].str.lower().values:
        return "Sorry! Movie not found."
    idx = data[data['movie_title'].str.lower() == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:11]
    recommended_movies = [data['movie_title'][i[0]] for i in sorted_scores]
    return recommended_movies

# UI Design
st.title("🎬 Movie Recommender System")

with st.expander("📚 How it works"):
    st.write("This system recommends movies based on content similarity using NLP and cosine similarity on textual data like genre, director, cast, etc.")

# Movie input
movie_input = st.text_input("Enter a movie name:", placeholder="e.g., Inception")

if st.button("🔍 Get Recommendations"):
    if not movie_input.strip():
        st.warning("Please enter a movie name.")
    else:
        results = get_recommendations(movie_input)
        if isinstance(results, str):
            st.error(results)
        else:
            st.subheader("✨ Recommended Movies:")
            for i, title in enumerate(results, 1):
                st.write(f"{i}. {title}")

# Optional: Suggest movie names
with st.expander("📖 View all available movie titles"):
    st.markdown("Here are a few sample titles you can try:")
    if data is not None:
        sample_titles = list(data['movie_title'].sample(20).values)
        st.write(", ".join(sample_titles))




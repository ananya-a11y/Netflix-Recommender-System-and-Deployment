import streamlit as st
import pandas as pd
import pickle
import requests
import bz2
import os
from pathlib import Path
import numpy as np

# Page config
st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS to improve appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #E50914;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .movie-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 10px;
        background-color: rgba(20, 20, 20, 0.8);
    }
    
    .movie-title {
        font-size: 1.2rem;
        color: white;
        margin-top: 0.5rem;
    }
    
    .recommendation-text {
        font-size: 1.8rem;
        color: #E50914;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'movie_list' not in st.session_state:
    st.session_state['movie_list'] = []
if 'similarity' not in st.session_state:
    st.session_state['similarity'] = None
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False

# Function to fetch movie poster
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=b9bf452c3871ecb61c8761a66d155cc8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        return None
    except Exception as e:
        st.warning(f"Could not fetch poster: {e}")
        return None

# Load data with proper error handling and caching
@st.cache_data
def load_movie_data():
    try:
        # If we previously saved an optimized version, load that instead
        if os.path.exists('optimized_movies.pkl'):
            with open('optimized_movies.pkl', 'rb') as f:
                return pickle.load(f)
        
        # Otherwise, load and optimize the CSV data
        movies = pd.read_csv('tmdb_5000_movies.csv')
        credits = pd.read_csv('tmdb_5000_credits.csv')
        
        # Optimize memory usage by converting data types
        for col in movies.select_dtypes(include=['object']).columns:
            if col not in ['title', 'overview', 'tagline']:
                movies[col] = movies[col].astype('category')
        
        movies = movies.merge(credits, on='title')
        
        # Keep only necessary columns
        movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
        
        # Save the optimized dataframe for future use
        with open('optimized_movies.pkl', 'wb') as f:
            pickle.dump(movies, f)
            
        return movies
    except Exception as e:
        st.error(f"Error loading movie data: {e}")
        return None

# Function to load or compute similarity matrix
@st.cache_data
def get_similarity_matrix():
    try:
        # Try to load pre-computed similarity matrix if it exists
        if os.path.exists('similarity.pbz2'):
            with bz2.BZ2File('similarity.pbz2', 'rb') as f:
                return pickle.load(f)
        
        # If we have a non-compressed version, load that
        if os.path.exists('similarity.pkl'):
            with open('similarity.pkl', 'rb') as f:
                return pickle.load(f)
                
        # If no similarity matrix exists, inform the user
        st.warning("Similarity matrix not found. Please generate it first.")
        return None
    except Exception as e:
        st.error(f"Error loading similarity matrix: {e}")
        return None

# Recommendation function
def recommend(movie_title, movies_df, similarity_matrix):
    try:
        if movie_title not in movies_df['title'].values:
            return []
        
        movie_index = movies_df[movies_df['title'] == movie_title].index[0]
        distances = similarity_matrix[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_movies = []
        for i in movie_list:
            movie_id = movies_df.iloc[i[0]].movie_id
            recommended_movies.append({
                'title': movies_df.iloc[i[0]].title,
                'poster': fetch_poster(movie_id)
            })
        return recommended_movies
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return []

# Main function to run the Streamlit app
def main():
    st.markdown("<h1 class='main-header'>Netflix Movie Recommender System</h1>", unsafe_allow_html=True)
    
    # Show a spinner while loading data
    with st.spinner("Loading movie data... This may take a moment."):
        if not st.session_state['data_loaded']:
            # Load movie data
            movies_df = load_movie_data()
            if movies_df is None:
                st.error("Failed to load movie data. Please check your dataset files.")
                st.stop()
            
            # Load similarity matrix
            similarity_matrix = get_similarity_matrix()
            if similarity_matrix is None:
                st.error("Similarity matrix not found or could not be loaded.")
                st.warning("Please ensure you've pre-computed the similarity matrix.")
                st.stop()
            
            # Store in session state
            st.session_state['movie_list'] = sorted(movies_df['title'].tolist())
            st.session_state['similarity'] = similarity_matrix
            st.session_state['movies_df'] = movies_df
            st.session_state['data_loaded'] = True
    
    # Create the selection box for movies
    selected_movie = st.selectbox(
        "Select or type a movie you like",
        st.session_state['movie_list']
    )
    
    # Create a button for getting recommendations
    if st.button("Get Recommendations"):
        with st.spinner("Finding movies you'll love..."):
            recommendations = recommend(
                selected_movie, 
                st.session_state['movies_df'], 
                st.session_state['similarity']
            )
            
            if recommendations:
                st.markdown("<h2 class='recommendation-text'>Recommended Movies</h2>", unsafe_allow_html=True)
                
                # Display recommendations in a grid
                cols = st.columns(5)
                for i, movie in enumerate(recommendations):
                    with cols[i]:
                        if movie['poster']:
                            st.image(movie['poster'], width=150)
                        else:
                            st.image("https://via.placeholder.com/150x225?text=No+Poster", width=150)
                        st.markdown(f"<p class='movie-title'>{movie['title']}</p>", unsafe_allow_html=True)
            else:
                st.warning("Could not generate recommendations. Please try another movie.")

# Run the app
if __name__ == '__main__':
    main()



import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load the data
df = pd.read_csv('final_df.csv')

# Generate TF-IDF matrix
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['tags'])

# Compute cosine similarity
similarity = cosine_similarity(tfidf_matrix)

# Save similarity matrix to the same folder (root)
with open('similarity.pkl', 'wb') as f:
    pickle.dump(similarity, f)

print("✅ similarity.pkl generated in current folder.")

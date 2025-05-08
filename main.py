import numpy as np
import pandas as pd
from flask import Flask, render\_template, request, jsonify
from sklearn.feature\_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine\_similarity
import pickle
import os

app = Flask(**name**, template\_folder='templates')

# Load ML model and vectorizer

try:
clf = pickle.load(open('nlp\_model.pkl', 'rb'))
vectorizer = pickle.load(open('transform.pkl','rb'))
except Exception as e:
print(f"Model loading error: {e}")
clf, vectorizer = None, None

# Load data and compute similarity only ONCE

try:
data = pd.read\_csv('main\_data.csv')
cv = CountVectorizer()
count\_matrix = cv.fit\_transform(data\['comb'])
similarity = cosine\_similarity(count\_matrix)

except Exception as e:
print(f"Error loading main\_data.csv or computing similarity: {e}")
data, similarity = None, None

def get\_suggestions():
try:
return list(data\['movie\_title'].str.capitalize())
except:
return \[]

def rcmd(movie):
movie = movie.lower()
if movie not in data\['movie\_title'].str.lower().values:
return 'Sorry! Try another movie name.'
i = data.loc\[data\['movie\_title'].str.lower() == movie].index\[0]
lst = sorted(list(enumerate(similarity\[i])), key=lambda x: x\[1], reverse=True)\[1:11]
return \[data\['movie\_title']\[i\[0]] for i in lst]

@app.route('/', methods=\['GET', 'HEAD'])
@app.route('/home', methods=\['GET', 'HEAD'])
def home():
try:
suggestions = get\_suggestions()
return render\_template('home.html', suggestions=suggestions)
except Exception as e:
return f"Error rendering home.html: {e}", 500

@app.route("/similarity", methods=\["POST"])
def get\_similarity():
movie = request.form.get('name')
if not movie:
return jsonify({"error": "No movie name provided."})
recs = rcmd(movie)
if isinstance(recs, str):
return jsonify({"error": recs})
return jsonify({"recommendations": recs})

@app.route("/recommend", methods=\["POST"])
def recommend():
try:
details = {key: request.form\[key] for key in request.form}
suggestions = get\_suggestions()
for k in \['rec\_movies', 'rec\_posters', 'cast\_names', 'cast\_chars', 'cast\_profiles', 'cast\_bdays', 'cast\_bios', 'cast\_places']:
if k in details:
details\[k] = details\[k].split('","')
details\[k]\[0] = details\[k]\[0].replace('\["', '')
details\[k]\[-1] = details\[k]\[-1].replace('"]', '')
cast\_ids = details\['cast\_ids'].strip('\[]').split(',')
movie\_cards = {details\['rec\_posters']\[i]: details\['rec\_movies']\[i] for i in range(len(details\['rec\_movies']))}
casts = {details\['cast\_names']\[i]: \[cast\_ids\[i], details\['cast\_chars']\[i], details\['cast\_profiles']\[i]] for i in range(len(details\['cast\_names']))}
cast\_details = {details\['cast\_names']\[i]: \[cast\_ids\[i], details\['cast\_profiles']\[i], details\['cast\_bdays']\[i], details\['cast\_places']\[i], details\['cast\_bios']\[i]] for i in range(len(details\['cast\_names']))}

```
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
    return f"Error in /recommend: {e}", 500
```

if **name** == '**main**':
port = int(os.environ.get("PORT", 10000))
app.run(host='0.0.0.0', port=port)


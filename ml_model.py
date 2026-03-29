import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle

print("🚀 Training started...")

# LOAD DATA
data = pd.read_csv("dataset.csv")

X = data['input']
y = data['label']

# TF-IDF (better than CountVectorizer)
vectorizer = TfidfVectorizer()
X_vector = vectorizer.fit_transform(X)

# RANDOM FOREST (better accuracy)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_vector, y)

# SAVE
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Real ML Model Trained Successfully!")
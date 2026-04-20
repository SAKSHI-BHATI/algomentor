import json
import os
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL_PATH = "AI_engine/trained_models/pseudocode_model"
os.makedirs(MODEL_PATH, exist_ok=True)

model = None
vectorizer = None


# ---------------- TRAIN ----------------
def train_model(dataset_path):
    with open(dataset_path, "r") as f:
        data = json.load(f)

    X = [d["input"] for d in data]
    y = [d["label"] for d in data]

    vec = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2)
    )

    X_vec = vec.fit_transform(X)

    clf = LogisticRegression(max_iter=2000)
    clf.fit(X_vec, y)

    joblib.dump(clf, os.path.join(MODEL_PATH, "model.pkl"))
    joblib.dump(vec, os.path.join(MODEL_PATH, "vectorizer.pkl"))

    print("✅ Pseudocode model trained")


# ---------------- LOAD ----------------
def load_model():
    global model, vectorizer

    if model is None:
        model = joblib.load(os.path.join(MODEL_PATH, "model.pkl"))
        vectorizer = joblib.load(os.path.join(MODEL_PATH, "vectorizer.pkl"))

    return model, vectorizer


# ---------------- PREDICT ----------------
def predict(code):
    clf, vec = load_model()

    X_vec = vec.transform([code])
    pred = clf.predict(X_vec)[0]

    return {
        "label": pred
    }


# ---------------- TEST ----------------
if __name__ == "__main__":
    sample = "for i in range(n): for j in range(n): if arr[i]==arr[j]"
    print(predict(sample))
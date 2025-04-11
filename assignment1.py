import json
import math
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict

nltk.download('stopwords')
nltk.download('wordnet')

stopword_set = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    return [lemmatizer.lemmatize(word) for word in re.findall(r"\w+", text.lower()) if word not in stopword_set]

def load_image_metadata(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    image_docs = {}
    metadata = {}
    for i, entry in enumerate(data, start=1):
        combined_text = f"{entry.get('alt', '')} {entry.get('title', '')} {entry.get('context', '')}"
        processed_text = preprocess_text(combined_text)
        image_docs[i] = processed_text
        metadata[i] = entry
    print(f"Loaded {len(image_docs)} image metadata entries.")
    return image_docs, metadata

def build_inverted_index(doc_store):
    index = defaultdict(lambda: defaultdict(int))
    total_documents = len(doc_store)
    for doc_id, terms in doc_store.items():
        for term in set(terms):
            index[term][doc_id] = terms.count(term)
    idf_scores = {word: math.log((total_documents + 1) / (1 + len(index[word])) + 1) for word in index}
    return index, idf_scores

def compute_tfidf(index, idf_scores):
    return {term: {doc_id: ((1 + math.log(freq)) * idf_scores[term]) / (1 + len(docs))
                   for doc_id, freq in docs.items()} for term, docs in index.items()}

def bm25_score(query_terms, index, doc_lengths, avg_length, k1=1.5, b=0.75):
    scores = defaultdict(float)
    for term in query_terms:
        if term in index:
            idf = math.log((len(doc_lengths) - len(index[term]) + 0.5) / (len(index[term]) + 0.5) + 1)
            for doc_id, tf in index[term].items():
                score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_lengths[doc_id] / avg_length))))
                scores[doc_id] += score
    return scores

def vsm_score(query_terms, tfidf_matrix, doc_lengths):
    scores = defaultdict(float)
    for term in query_terms:
        if term in tfidf_matrix:
            for doc_id, weight in tfidf_matrix[term].items():
                scores[doc_id] += weight / (doc_lengths[doc_id] ** 0.5)
    return scores

def lm_score(query_terms, index, doc_lengths, mu=2000):
    scores = defaultdict(float)
    total_terms = sum(doc_lengths.values())
    for doc_id in doc_lengths:
        doc_length = doc_lengths[doc_id]
        for term in query_terms:
            term_freq = index[term].get(doc_id, 0) if term in index else 0
            p_w_C = sum(index[term].values()) / total_terms if term in index else 0
            score = math.log((term_freq + mu * p_w_C) / (doc_length + mu)) if (term_freq + mu * p_w_C) > 0 else 0
            scores[doc_id] += score
    return scores

from flask import Flask, render_template, request, jsonify
import os
from assignment1 import * 

app = Flask(__name__)

metadata_path = "static/image_metadata.json"
image_folder = "static/images"

documents, metadata = load_image_metadata(metadata_path)
inverted_index, idf_values = build_inverted_index(documents)
tfidf_matrix = compute_tfidf(inverted_index, idf_values)
doc_lengths = {doc_id: len(terms) for doc_id, terms in documents.items()}
avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query", "")
    model = request.form.get("model", "bm25")
    query_terms = preprocess_text(query)

    if not query_terms:
        return jsonify(results=[])

    if model == "bm25":
        scores = bm25_score(query_terms, inverted_index, doc_lengths, avg_doc_length)
    elif model == "vsm":
        scores = vsm_score(query_terms, tfidf_matrix, doc_lengths)
    elif model == "lm":
        scores = lm_score(query_terms, inverted_index, doc_lengths)
    else:
        scores = {}

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
    results = []
    for doc_id, score in ranked:
        entry = metadata.get(doc_id, {})
        entry["score"] = round(score, 4)
        entry["image_url"] = os.path.join("/static/images", entry.get("image", ""))
        results.append(entry)

    return jsonify(results=results)

if __name__ == "__main__":
    app.run(debug=True)

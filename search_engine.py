from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
import numpy as np
import streamlit as st
import requests
from utils import utils, exceptions
from utils.utils import downloadFile

model = SentenceTransformer("bert-base-nli-mean-tokens", cache_folder="cache_model")

#Loads the embeddings for the Congress bill model which powers the search engine, if it cannot be found it is downloaded from the database
def loadBillModel(path, update_status):
    if not os.path.exists(path) or update_status:
        downloadFile(path)

    print(f"Loading embeddings from {path}")
    with open(path, "rb") as file:
        cache_data = pickle.load(file)
        try:
            number = cache_data['number']
            type = cache_data['type']
            text = cache_data['text']
            embeddings = cache_data['embeddings']
        except KeyError:
            raise KeyError("Embeddings file is not formatted correctly")

    return model, number, type, text, embeddings


#Returns a cosine simliarity score numpy array corresponding to each individual embedding
def predict(sentence, *, model, embeddings):
    embeddings.shape

    test_sentence = model.encode(sentence)
    test_sentence.shape

    score = cosine_similarity(
    [test_sentence],
    embeddings
    )

    return score


#Returns search results for a bill by comparing it too thousands of Congress bills and returning the closest scores
def search(query, update_status, *, limit=10):
    model, number, type, text, embeddings = loadBillModel("search_embeddings.pkl", update_status)

    scores = predict(query, model=model, embeddings=embeddings)

    highScores = sorted(scores[0], reverse=True)[:limit]

    results = []
    for score in highScores:
        index = np.where(scores[0] == score)[0]
        results.append({"number": number[index[0]], "type": type[index[0]], "score": score})

    return results

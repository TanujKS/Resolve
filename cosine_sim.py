import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import os
import pickle
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import streamlit as st
import json

#folder = "reddit_data"


def getAverage(data):
    if not data:
        return None

    sum = 0
    for d in data:
        sum += d
    sum /= len(data)
    return sum


def createRedditModel(embedding_path):
    model = SentenceTransformer("bert-base-nli-mean-tokens")
    if not os.path.exists(embedding_path):
        remoteRedditModel()
        # print("Encoding the corpus. This might take a while")
        # df = pd.read_json(f"{raw_path}")
        #
        # df_sentences = df[['text']]
        # sentences = df_sentences['text'].to_list()
        #
        # sentence_embeddings = model.encode(sentences)
        #
        # print("Storing file on disc")
        # with open(f"{embedding_path}", "wb") as file:
        #     pickle.dump({'sentences': sentences, 'embeddings': sentence_embeddings}, file)

    else:
        print("Loading pre-computed embeddings from disc")
        with open(f"{embedding_path}", "rb") as file:
            cache_data = pickle.load(file)
            sentences = cache_data['sentences']
            sentence_embeddings = cache_data['embeddings']

    return model, sentences, sentence_embeddings


def createBillModel(embedding_path):
    model = SentenceTransformer("bert-base-nli-mean-tokens")

    if not os.path.exists(embedding_path):
        print("Downloading corpus")
        remoteBillModel()
        # print("Encoding the corpus. This might take a while")
        # df = pd.read_json(f"{raw_path}")
        #
        # df_id = df['id']
        # id = df_id.to_list()
        #
        # df_type = df['type']
        # type = df_type.to_list()
        #
        # df_sentences = df[['text']]
        # sentences = df_sentences['text'].to_list()
        #
        # sentence_embeddings = model.encode(sentences, show_progress_bar=True)
        #
        # print("Storing file on disc")
        # with open(f"{embedding_path}", "wb") as file:
        #     pickle.dump({'id': id, 'sentences': sentences, 'type': type, 'embeddings': sentence_embeddings}, file)

    print("Loading pre-computed embeddings from disc")
    with open(f"{embedding_path}", "rb") as file:
        cache_data = pickle.load(file)
        id = cache_data['id']
        type = cache_data['type']
        sentences = cache_data['sentences']
        sentence_embeddings = cache_data['embeddings']

    return model, id, type, sentences, sentence_embeddings


def remoteRedditModel():
    if not firebase_admin._apps:
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)

    bucket = storage.bucket("resolve-87f2f.appspot.com")

    blob = bucket.blob("reddit_embeddings.pkl")
    blob.download_to_filename("reddit_embeddings.pkl")

    print("Downloaded")

def remoteBillModel():
    if not firebase_admin._apps:
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)

     bucket = storage.bucket("resolve-87f2f.appspot.com")

     blob = bucket.blob("bill_embeddings.pkl")
     blob.download_to_filename("bill_embeddings.pkl")

     print("Downloaded storage object.")



#download_blob("hr_pruned.json", "test.json")

def predict(sentence, *, model, sentence_embeddings):
    #Returns a cosine simliarty score array corresponding to each sentence
    sentence_embeddings.shape

    test_sentence = model.encode(sentence)
    test_sentence.shape

    score = cosine_similarity(
    [test_sentence],
    sentence_embeddings
    )

    return score


def getRelevancy(bill, **kwargs):
    scores = predict(bill, **kwargs)[0].tolist()
    print(scores)
    return getAverage(scores)


def search(query):
    model, id, type, sentences, sentence_embeddings = createBillModel("bill_embeddings.pkl")

    scores = predict(query, model=model, sentence_embeddings=sentence_embeddings)

    highScores = sorted(scores[0], reverse=True)[:20]

    results = []
    for score in highScores:
        index = np.where(scores[0] == score)[0]
        results.append({"number": id[index[0]], "type": type[index[0]]})

    return results

if __name__ == "__main__":
    #model, sentences, sentence_embeddings = createRedditModel("reddit_data/post_embeddings.pkl", "reddit_data/data.json")
    createBillModel("bill_embeddings.pkl")
    #print(getRelevancy("to designate a post office", model=model, sentence_embeddings=sentence_embeddings))
# print("Created model")
# sentence_embeddings.shape
#
# test_sentence = model.encode("abortion")
# test_sentence.shape
#
# score = cosine_similarity(
# [test_sentence],
# sentence_embeddings
# )
#
# highScore = sorted(score[0], reverse=True)[5:]
# print(highScore)
#
# index = np.where(score[0] == highScore)
#
# #print(type(index[0][0]))
# print(id[index[0][0]])

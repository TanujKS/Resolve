import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import os
import pickle
from bill import Bill


def getAverage(data):
    sum = 0
    for d in data:
        sum += d
    sum /= len(data)
    return sum



def createModel():
    model = SentenceTransformer("bert-base-cased")
    if not os.path.exists("my-embeddings.pkl"):
        print("Encoding the corpus. This might take a while")
        df = pd.read_json("reddit_data/data.json")

        df_reddit = df[['title']]
        posts = df_reddit['title'].to_list()

        #posts = posts[0:5000]
        sentence_embeddings = model.encode(posts, show_progress_bar=True)

        print("Storing file on disc")
        with open("my-embeddings.pkl", "wb") as fOut:
            pickle.dump({'posts': posts, 'embeddings': sentence_embeddings}, fOut)

    else:
        print("Loading pre-computed embeddings from disc")
        with open("my-embeddings.pkl", "rb") as fIn:
            cache_data = pickle.load(fIn)
            posts = cache_data['posts']
            sentence_embeddings = cache_data['embeddings']

    return model, sentence_embeddings


def predict(sentence, *, model, sentence_embeddings):
    sentence_embeddings.shape

    test_sentence = model.encode(sentence)
    test_sentence.shape

    score = cosine_similarity(
    [test_sentence],
    sentence_embeddings
    )

    return getAverage(score[0])


model, sentence_embeddings = createModel()
print("Created model")

recentBills = Bill.recentBills(117, "hr", limit=100)
print("Got bills")
titles = [bill.title for bill in recentBills]
scores = {}
for title in titles:
    scores[title] = predict(title, model=model, sentence_embeddings=sentence_embeddings)

ranked = sorted(scores, key=lambda x: scores[x], reverse=True)

for rank in ranked:
    print(rank, scores[rank])
    print("\n\n")

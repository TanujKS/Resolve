import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.metrics.pairwise import cosine_similarity
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--encoder", help="Encodes models with different PyTorch devices", default="cuda")
parser.add_argument("-na", "--new-auth", help="Fetches a new auth token for Reddit's API", action="store_true")
args = parser.parse_args()

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
load_dotenv()

username = "garbage22507"
client_id = "yKxWouPF79VSwyXRWL4jJQ"
base_headers = {'user-agent': f'Windows PC:resolve:v1.0.0 (by /u/{username})'}
newAuth = args.new_auth
model = SentenceTransformer("bert-base-nli-mean-tokens")


def getAuthToken():
    auth = requests.auth.HTTPBasicAuth(client_id, os.getenv("REDDIT_SECRET"))

    data = {'grant_type': 'password',
            'username': username,
            'password': os.getenv("REDDIT_PASSWORD")}


    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=base_headers).json()

    TOKEN = res.get('access_token')
    if not TOKEN:
        raise Exception(res)

    print(TOKEN)
    return TOKEN


def writeAuthToken(token):
    password = os.getenv("REDDIT_PASSWORD")
    secret = os.getenv("REDDIT_SECRET")

    with open(".env", "w+") as file:
        file.write(f"REDDIT_SECRET={secret}\nREDDIT_PASSWORD={password}\nREDDIT_API_KEY={token}")

    load_dotenv()


def df_from_response(data_list, res):
    count = 0
    for post in res['data']['children']:
        data_list.append({
            'title': post['data']['title'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            "id": post['data']['id'],
            'created_utc': datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'kind': post['kind'],
            })
        count += 1
    return data_list, count


def fetchData(sub, total, newAuth=False):
    print("New Auth:", newAuth)

    if newAuth:
        token = getAuthToken()
        writeAuthToken(token)
    else:
        token = os.environ.get("REDDIT_API_KEY")
        print(token)

    headers = {**base_headers, **{'Authorization': f"bearer {token}"}}
    params = {"limit": "100", "t": "all"}
    data_list = []
    totalIters = int(total/100)

    for i in range(totalIters):
        # make request
        res = requests.get(f"https://oauth.reddit.com/r/{sub}", headers=headers, params=params)
        #print(res.text)
        res = res.json()

        if not res['data'].get('children'):
            break

        data_list, count = df_from_response(data_list, res)
        row = data_list[len(data_list)-1]


        fullname = row['kind'] + '_' + row['id']

        params['after'] = fullname

        print(f"Added {count} entries")
        print(f"Total Entries: {len(data_list)} entries")
        print("\n")


    print("Total Entries:", len(data_list))

    df = pd.DataFrame.from_records(data_list)
    df = df[['title']]
    df = df.rename(columns={"title": "text"})

    print(df.head())

    return df


def createRedditEmbeddings(df, output_path=None):
    df_posts = df[['text']]
    posts = df_posts['text'].to_list()

    model = SentenceTransformer("bert-base-nli-mean-tokens")

    print(f"Encoding the corpus with {len(df.index)} entries. This might take a while...")
    post_embeddings = model.encode(posts, show_progress_bar=True, device=args.encoder)

    if output_path:
        print(f"Saving embeddings to {output_path}")

        with open(output_path, "wb") as file:
            pickle.dump({'posts': posts, 'embeddings': post_embeddings}, file)

    return post_embeddings

#Delete after done
def loadRedditEmbeddings(path="reddit_embeddings.pkl"):
    print(f"Loading embeddings from {path}")
    with open(path, "rb") as file:
        cache_data = pickle.load(file)
        posts = cache_data.get('posts')
        post_embeddings = cache_data.get('embeddings')

        if not posts or not post_embeddings.any():
            raise exceptions.EmbeddingError("Embedding pkl is not formatted correctly.")

    return model, number, type, text, embeddings


def predict(sentence, *, model, embeddings):
    embeddings.shape

    test_sentence = model.encode(sentence)
    test_sentence.shape

    score = cosine_similarity(
    [test_sentence],
    embeddings
    )

    return score


#Determines how relevant a bill is by comparing it to thousands of up-to-date posts from Reddit's r/Politics and returning the average similarity
def getRelevancy(bill, **kwargs):
    scores = predict(bill, **kwargs)[0].tolist()
    return np.average(scores)


def rankCollection(embeddings, coll_ref, scores=[], cursor=None):

    if cursor is not None:
        docs = [snapshot.reference for snapshot
                in coll_ref.limit(1000).order_by("__name__").start_after(cursor).stream()]
    else:
        docs = [snapshot.reference for snapshot
                in coll_ref.limit(1000).order_by("__name__").stream()]

    for doc in docs:
        data = doc.get().to_dict()
        text = data.get('text', '')

        data['relevancy_score'] = getRelevancy(text, model=model, embeddings=embeddings)

        print(data['relevancy_score'])
        scores.append(data)

    if len(docs) == 1000:
        return rankCollection(embeddings, coll_ref, scores, docs[999].get())
    else:
        return scores


def rankBills(embeddings):
    collections = db.collection("congress_data").document("117").collections()
    scores = []
    for collection in collections:
        print("\n\n\n\n")
        print(collection.id)
        scores = rankCollection(embeddings, collection, scores)
    return sorted(scores, key=lambda x: x['relevancy_score'], reverse=True)


def addBills(collection, data):
    for i in range(0, len(data) - 1):
        collection.document(str(i)).set(data[i])


def main():
    df1 = fetchData("Politics/top", 5000, newAuth=newAuth)
    df2 = fetchData("Politics/hot", 5000)
    df = pd.concat([df1, df2])
    df.reset_index(inplace=True)
    embeddings = createRedditEmbeddings(df, output_path="reddit_embeddings.pkl")
    #embeddings = loadRedditModel()
    scores = rankBills(embeddings)
    addBills(db.collection("relevant_bills"), scores[0:250])


if __name__ == "__main__":
    main()

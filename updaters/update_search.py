import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import firebase_admin
from google.cloud import storage as gcs
from firebase_admin import credentials, firestore, storage
gcs.blob._MAX_MULTIPART_SIZE = 5 * 1024* 1024


cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {'storageBucket': "resolve-87f2f.appspot.com"})
db = firestore.client()
model = SentenceTransformer("bert-base-nli-mean-tokens")

def createBillDf(collection):
    bills = []
    for congress in collection.stream():
        for type in congress.reference.collections():
            count = 0
            for bill in type.stream():
                bill_data = bill.to_dict()
                bills.append(bill_data)
                count += 1
            print(f"{count} bills of type {type.id}")

    df = pd.DataFrame.from_records(bills)
    print(len(df.index), "total bills")
    return df


def createBillModel(df, output_path=None):
    df_number= df['number']
    number = df_number.to_list()

    df_type = df['type']
    type = df_type.to_list()

    df_text = df[['text']]
    text = df_text['text'].to_list()


    print("Encoding the corpus. This might take a while...")
    embeddings = model.encode(text, show_progress_bar=True)

    serialized_data = pickle.dumps({'number': number, 'text': text, 'type': type, 'embeddings': embeddings})

    if output_path:
        print(f"Saving embeddings to {output_path}")
        with open(output_path, "wb") as file:
            file.write(serialized_data)

    return serialized_data


def loadBillEmbeddings(path):
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

    return embeddings


def upload(input, output_path, *, path=False):
    bucket = storage.bucket()
    blob = bucket.blob(output_path)
    blob._chunk_size = 5 * 1024* 1024

    if path:
        blob.upload_from_filename(input_path)
    else:
        blob.upload_from_string(input)

    print(f"Uploaded to remote path: {output_path}")


def main():
    collection = db.collection("congress_data")
    df = createBillDf(collection)
    data = createBillModel(df, output_path="safety.pkl")
    #embeddings = loadBillEmbeddings("search_embeddings.pkl")
    upload(data, "search_embeddings.pkl")
    db.collection("congress_data").document("update_status").set({"updated": True})

if __name__ == "__main__":
    main()

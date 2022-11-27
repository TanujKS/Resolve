import json
import requests
import time
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

type = "sres"
congress = "117"
resume = 0


def load_data():
    with open(f"congress_data/{type}/{type}_pruned.json") as file:
        return json.load(file)


def findIndex(number):
    data = load_data()
    for bill in data:
        if bill['number'] != str(resume):
            continue

        return data.index(bill)
    else:
        return 0


def main():
    data = load_data()

    index = findIndex(resume)

    for i in range(index, len(data)):
        bill = data[i]

        print(bill['number'])

        bill['congress'] = congress
        bill['type'] = type

        byte_count = len(bill['text'].encode('utf8'))
        if byte_count > 1000000:
            continue

        doc = db.collection("congress_data").document(bill['congress']).collection(bill['type']).document(bill['number']).set(bill)


if __name__ == "__main__":
    main()

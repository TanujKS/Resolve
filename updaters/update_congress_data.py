import sys
sys.path.insert(0, "..")
import requests
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
from bill import Bill
from utils import exceptions
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--congress", help="Starts updating at a certain Congress session", default=117)
args = parser.parse_args()

types_of_legislation = ["hr", "s", "hjres","sjres", "hconres", "sconres", "hres", "sres"]
congresses = [i for i in (range(int(args.congress), 81, -1))]
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def build_database():
    for congress in congresses:
        print("Creating congress", congress)
        doc = db.collection("congress_data").document(str(congress))
        doc.set({})
        for type in types_of_legislation:
            doc.collection(type).document("0").set({})


def addData(bills, url):
    data = requests.get(url).json()

    if not data.get('summaries'):
        return bills

    for bill in data['summaries']:
        bill_data = bill['bill']

        title = bill_data['title']
        summary = bill['text']
        summary = Bill.pruneText(summary)

        if summary.startswith(title):
            summary = summary[len(title):].lstrip()

        bill_data['summary'] = summary
        bills.append(bill_data)

    if data['pagination'].get('next'):
        print("Fetched", data['pagination']['count'], "bills")
        return addData(bills, data['pagination']['next'])
    else:
        return bills


def fetchBills(congress, type):
    bills = addData([], f"https://api.congress.gov/v3/summaries/{congress}/{type}?fromDateTime=1980-01-03T00:00:00Z&toDateTime=2023-01-03T00:00:00Z&limit=250&{Bill.apikey_header}")
    return bills


def removeDuplicates(bills):
    numbers = []
    no_duplicates = []
    for bill in bills:
        if bill['number'] in numbers:
            continue

        numbers.append(bill['number'])
        no_duplicates.append(bill)

    return no_duplicates


def fetchDBBills(collection):
    bills = [bill.to_dict() for bill in collection.stream()]
    if not all(bills):
        return []
    return bills


def addBill(bill_data):
    bill = Bill.from_dict(bill_data)
    try:
        bill.text = bill.getText()

    except exceptions.NoText:
        print('No Text Available')
        return

    if not bill.text:
        return
        
    byte_count = len(bill.text.encode('utf8'))
    if byte_count < 1000000:
        doc = db.collection("congress_data").document(str(bill.congress)).collection(bill.type).document(str(bill.number))
        doc.set(bill.to_dict())


def updateBills(congress, type):
    db_bills = fetchDBBills(db.collection("congress_data").document(congress).collection(type))
    db_numbers = [bill['number'] for bill in db_bills]
    print(len(db_numbers), type, "bills in database")

    live_bills = removeDuplicates(fetchBills(int(congress), type))
    bill_numbers = [bill['number'] for bill in live_bills]
    print(len(bill_numbers), type, "bills in Congress")

    missing_bills = list(set(bill_numbers).difference(db_numbers))
    print(len(missing_bills), type, "bills to be added")

    for bill_data in live_bills:
        if bill_data['number'] in missing_bills:
            addBill(bill_data)
            print("Added bill", bill_data['type'], bill_data['number'])
    db.collection("congress_data").document(congress).collection(type).document("0").delete()


def main():
    for congress in congresses:
        print("Updating congress", congress)
        for type in db.collection("congress_data").document(str(congress)).collections():
            updateBills(str(congress), type.id)


if __name__ == "__main__":
    main()

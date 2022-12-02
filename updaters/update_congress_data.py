import sys
sys.path.insert(0, "..")
import requests
import json
from bill import Bill
import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def addData(bills, url):
    url += f"&limit=250&{Bill.apikey_header}"
    data = requests.get(url).json()

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


def fetchBills(type):
    congress = 117
    bills = addData([], f"https://api.congress.gov/v3/summaries/{congress}/{type}?fromDateTime=2022-01-03T00:00:00Z&toDateTime=2023-01-03T00:00:00Z")
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
    return bills


def addBill(bill_data):
    bill = Bill.from_dict(bill_data)
    bill.text = bill.getText()
    byte_count = len(bill.text.encode('utf8'))
    if byte_count < 1000000:
        doc = db.collection("congress_data").document(str(bill.congress)).collection(bill.type).document(str(bill.number))
        doc.set(bill.to_dict())


def updateBills(type):
    db_bills = fetchDBBills(db.collection("congress_data").document("117").collection(type))
    db_numbers = [bill['number'] for bill in db_bills]
    print(len(db_numbers), type, "bills in database")

    live_bills = removeDuplicates(fetchBills(type))
    bill_numbers = [bill['number'] for bill in live_bills]
    print(len(bill_numbers), type, "bills in Congress")

    missing_bills = list(set(bill_numbers).difference(db_numbers))
    print(len(missing_bills), type, "bills to be added")

    for bill_data in live_bills:
        if bill_data['number'] in missing_bills:
            addBill(bill_data)
            print("Added bill", bill_data['number'])

def main():
    for type in db.collection("congress_data").document("117").collections():
        updateBills(type.id)
    #updateBills("s")

if __name__ == "__main__":
    main()

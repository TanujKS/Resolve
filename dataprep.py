from bill import Bill
import exceptions

import requests
import os
import shutil
import json


def addData(tuning_data: dict, url):
    print(url)
    url += f"&limit=250&{Bill.apikey_header}"
    data = requests.get(url).json()
    for summary in data['summaries']:
        tuning_data.append({
        "title": summary['bill']['title'],
        "number": summary['bill']['number'],
        "summary": Bill.cleanSummary(summary['text'])
        })
    if data['pagination'].get('next'):
        return addData(tuning_data, data['pagination']['next'])
    else:
        return tuning_data


def fineTuneSummaries():
    tuning_data = []
    tuning_data = addData(tuning_data, f"https://api.congress.gov/v3/summaries/117/hr?fromDateTime=2021-01-03T00:00:00Z&toDateTime=2022-01-03T00:00:00Z&sort=updateDate+asc")

    with open("tuning_data.json", "w+") as file:
        json.dump(tuning_data, file, indent=4)


def fineTuneTexts():
    bigBills = []
    smallBills = []

    i = 0

    src = f"{os.getcwd()}/tuning_data_text.json"
    dst = f"{os.getcwd()}/temp.json"
    shutil.copy(src, dst)

    with open("temp.json") as file:
        tuning_data = json.load(file)

        for data in tuning_data:
            if data.get('text'):
                continue

            print(data['title'])

            if i == 20:
                with open("tuning_data_text.json", "w+") as textFile:
                    print("\n\nDumping")
                    json.dump(tuning_data, textFile, indent=4)
                    i = 0
            data['text'] = Bill.getTextOnly(117, "hr", data['number'])
            i += 1


def count():
    with open("tuning_data_text.json") as file:
        tuning_data = json.load(file)
        dataset = []

        big = 0
        small = 0
        for data in tuning_data:
            if not data['text']:
                break

            if len(data['text']) > 10000:
                big += 1
            else:
                small += 1

        print(len(tuning_data), "bills")
        print(f"{big} bills too large too process")
        print(f"{small} bills remaining")


def prepareData():
    with open("tuning_data_text.json") as file:
        tuning_data = json.load(file)
        dataset = []

        for data in tuning_data:
            if not data['text']:
                break

            if len(data['text']) < 10000:
                dataset.append({
                "prompt": f"Write a concise summary about the following bill: {data['text']}",
                "completion": data['summary']
                })

    with open("dataset.jsonl", "w+") as file:
        for data in dataset:
            json.dump(data, file)
            file.write("\n")

if __name__ == "__main__":
    fineTuneTexts()

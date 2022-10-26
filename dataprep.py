import bill
from bill import Bill
from utils import exceptions

import requests
import os
import shutil
import json
import random
import argparse


def addSummary(tuning_data: dict, url):
    url += f"&limit=250&{Bill.apikey_header}"
    data = requests.get(url).json()

    for summary in data['summaries']:
        print(summary['bill']['title'])
        tuning_data.append({
        "title": summary['bill']['title'],
        "number": summary['bill']['number'],
        "summary": summary['text']
        })


    if data['pagination'].get('next'):
        return addSummary(tuning_data, data['pagination']['next'])
    else:
        return tuning_data


def fetchSummaries(type):
    congress = 117
    tuning_data = []
    tuning_data = addSummary(tuning_data, f"https://api.congress.gov/v3/summaries/{congress}/{type}?fromDateTime=2021-01-03T00:00:00Z&toDateTime=2022-01-03T00:00:00Z")

    with open(f"data/{type}_raw_summary.json", "w+") as file:
        json.dump(tuning_data, file, indent=4)
#
#
# def pruneEntry(number):
#     src = "data/tuning_data_text_raw.json"
#
#     with open(src) as file:
#         tuning_data = json.load(file)
#
#         for entry in tuning_data:
#             if entry.get('number', 0) == str(number):
#                 data = {}
#
#                 for key, item in entry.items():
#                     data[key] = Bill.pruneText(item)
#
#                     if key == "text":
#                         data['text'] = Bill.cleanRawText(data['text'])
#
#                     if key == "summary":
#                             summary = data['summary']
#                             title = data['title']
#
#                             if summary.startswith(title):
#                                 data['summary'] = summary[len(title):].lstrip()
#
#                     if key != "number" and key != "title":
#                         data[key] = Bill.addPeriod(data[key])
#
#
#                 return data


def pruneData():
    src = "data/tuning_data_text_raw.json"
    dest = "data/tuning_data_pruned.json"

    with open(src) as file:
        tuning_data = json.load(file)
        pruned_data = []

        for entry in tuning_data:
            if not entry.get('text'):
                break

            data = {}

            for key, item in entry.items():
                data[key] = Bill.pruneText(item)


                if key == "summary":
                        summary = data['summary']
                        title = data['title']

                        if summary.startswith(title):
                            data['summary'] = summary[len(title):].lstrip()

                if key != "number" and key != "title":
                    data[key] = Bill.addPeriod(data[key])


                if key == "text":
                    data['text'] = Bill.cleanRawText(data['text'])


            pruned_data.append(data)

    with open(dest, "w+") as file:
        json.dump(pruned_data, file, indent=4)


def dump(path, data):
    with open(path, "w+") as file:
        print("\n\nDumping")
        json.dump(data, file, indent=4)


def fetchTexts(type, file="text"):
    bigBills = []
    smallBills = []

    i = 0

    src = f"{os.getcwd()}/data/{type}_raw_{file}.json"
    dst = f"{os.getcwd()}/data/temp.json"
    shutil.copy(src, dst)

    with open("data/temp.json") as file:
        tuning_data = json.load(file)

        for data in tuning_data:
            if data.get('text'):
                if not "JavaScript" in data['text']:
                    continue


            print(data['title'])

            if i == 20:
                dump(f"data/{type}_raw_text.json", tuning_data)

            bill = Bill(117, type, data['number'])
            rawText = bill.getRawText()

            if rawText:
                if "JavaScript" in rawText:
                    raise RateLimited()
            data['text'] = rawText
            i += 1
        dump(f"data/{type}_raw_text.json", tuning_data)

def count(file):
    with open(f"data/{file}.json") as file:
        tuning_data = json.load(file)
        dataset = []

        big = 0
        small = 0
        for data in tuning_data:
            if not data.get('text'):
                break

            if len(data['text']) > 20000:
                big += 1
            else:
                small += 1

        print(len(tuning_data), "bills")
        print(f"{big} bills too large too process")
        print(f"{small} bills remaining")
        print(f"Estimated Price: ${(small/500) * 8}")


def verifyTexts():
    with open("data/tuning_data_pruned.json") as file:
        tuning_data = json.load(file)

        index = random.randint(0, len(tuning_data))
        data = tuning_data[index]

        print(
        "Title:", data['title'],
        "\n",
        "Summary", data['summary'],
        "\n",
        "Text", data['text']
        )

def buildDataset(limit=None):
    with open("data/tuning_data_pruned.json") as file:
        tuning_data = json.load(file)
        dataset = []

        if not limit:
            limit = len(tuning_data) - 1

        tokens = 0
        for index in range(0, limit):
            data = tuning_data[index]

            tokens += (len(data['text'])/4)
            tokens += (len(data['summary'])/4)

            dataset.append({
            "prompt": data['text'],
            "completion": data['summary']
            })

        print(f"{len(dataset)} examples")
        print("Estimated Price:", (tokens/1000) * 0.003)

    with open("data/dataset.jsonl", "w+") as file:
        for data in dataset:
            json.dump(data, file)
            file.write("\n")


if __name__ == "__main__":
    #pruneTexts()
    #count()
    #pruneText(2393)
    #buildDataset(2000)
    #count()
    fetchTexts("hres", file="summary")

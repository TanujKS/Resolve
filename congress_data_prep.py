import bill
from bill import Bill
from utils import utils
from utils import exceptions

import pandas as pd
import requests
import os
import shutil
import json
import random
import argparse
from transformers import GPT2TokenizerFast
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

folder = "congress_data"

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

    with open(f"{folder}/{type}/{type}_raw_summary.json", "w+") as file:
        json.dump(tuning_data, file, indent=4)


def dump(path, data):
    with open(path, "w+") as file:
        print("\n\nDumping")
        json.dump(data, file, indent=4)


def fetchText(type, file="text"):
    bigBills = []
    smallBills = []

    i = 0

    src = f"{os.getcwd()}/{folder}/{type}/{type}_raw_{file}.json"
    copy_dst = f"{os.getcwd()}/{folder}/temp.json"
    shutil.copy(src, copy_dst)

    with open(f"{folder}/temp.json") as file:
        tuning_data = json.load(file)

        for data in tuning_data:
            if data.get('text'):
                if not "JavaScript" in data['text']:
                    continue


            print(data['title'])

            if i == 20:
                dump(f"{folder}/{type}/{type}_raw_text.json", tuning_data)

            bill = Bill(117, type, data['number'])
            rawText = bill.getRawText()

            if rawText:
                if "JavaScript" in rawText:
                    raise RateLimited()
            data['text'] = rawText
            i += 1

        dump(f"{folder}/{type}/{type}_raw_text.json", tuning_data)


def fetchTexts():
    types = [key for key, item in Bill.types_of_legislation.items()]
    for type in types:
        print(type, "\n\n\n\n")
        fetchText(type)


def pruneAllData():
    types = [key for key, item in Bill.types_of_legislation.items()]
    for type in types:
        print(type, "\n\n")
        pruneData(type)


def pruneData(type):
    src = f"{folder}/{type}/{type}_raw_text.json"
    dest = f"{folder}/{type}/{type}_pruned.json"

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
                    data[key] = utils.addPeriod(data[key])


                if key == "text":
                    data['text'] = Bill.cleanRawText(data['text'])

            data['id'] = data['number']
            data['type'] = type
            pruned_data.append(data)

    df = pd.DataFrame.from_records(pruned_data)

    with open(dest, "w+") as file:
        file.write(df.to_json())


def combine():
    types = [key for key, item in Bill.types_of_legislation.items()]
    dfs = []
    for type in types:
        df = pd.read_json(f"congress_data/{type}/{type}_pruned.json")
        dfs.append(df)

    df = pd.concat(dfs)
    print(df.tail())
    df.reset_index(inplace=True)

    with open(f"{folder}/data.json", "w+") as file:
        file.write(df.to_json())


def removeDuplicates(type):
    with open(f"{folder}/{type}/{type}_pruned.json") as file:
        data = json.load(file)
        new_data = []
        numbers = []

        for entry in data:
            if entry['number'] in numbers:
                continue

            new_data.append(entry)
            numbers.append(entry['number'])

    with open(f"{folder}/{type}/{type}_pruned.json", "w+") as file:
        json.dump(new_data, file, indent=4)


def verifyData(type):
    with open(f"{folder}/{type}/{type}_pruned.json") as file:
        pruned_data = json.load(file)

        index = random.randint(0, len(pruned_data) - 1)
        data = pruned_data[index]

        print(
        "Title:", data['title'],
        "\n",
        "Summary", data['summary'],
        "\n",
        "Text", data['text']
        )


def count():
    types = [key for key, item in Bill.types_of_legislation.items()]
    totalTokens = 0
    totalBig = 0
    totalSmall = 0

    for type in types:
        with open(f"{folder}/{type}/{type}_pruned.json") as file:
            tuning_data = json.load(file)
            dataset = []

            big = 0
            small = 0

            for data in tuning_data:
                if not data.get('text'):
                    break

                tokens = len(tokenizer(data['text'])['input_ids'])

                if tokens > 4096:
                    big += 1
                else:
                    small += 1
                    totalTokens += tokens
                    totalTokens += len(tokenizer(data['summary'])['input_ids'])

            totalBig += big
            totalSmall += small
            print(len(tuning_data), type, "bills")
            print(f"{big} bills too large too process")
            print(f"{small} bills remaining")
            print("\n\n")
    totalTokens *= 4

    print(f"Estimated Price: ${(totalTokens/1000)*0.003}")


def buildTuningDataset(limit=None):
    types = [key for key, item in Bill.types_of_legislation.items()]
    dataset = []

    for type in types:

        with open(f"{folder}/{type}/{type}_pruned.json") as file:
            tuning_data = json.load(file)

            if not limit:
                limit = len(tuning_data) - 1

            tokens = 0
            for index in range(0, limit):
                data = tuning_data[index]

                tokens += len(tokenizer(data['text'])['input_ids'])
                tokens += len(tokenizer(data['summary'])['input_ids'])

                dataset.append({
                "prompt": data['text'],
                "completion": data['summary']
                })

            print(f"{len(dataset)} examples")
            print("Estimated Price:", (tokens/1000) * 0.003)

        with open(f"{folder}/dataset.jsonl", "w+") as file:
            for data in dataset:
                json.dump(data, file)
                file.write("\n")


if __name__ == "__main__":
    #fetchSummaries("hres")
    #fetchTexts("hr")
    #pruneAllData()
    #combine()
    #pruneData("hr")
    #removeDuplicates("hconres")
    #verifyData("sjres")
    #count()
    #buildDataset()
    #data = findLarge("hr")
    #print(data)
    fetchTexts()

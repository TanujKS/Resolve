import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import pandas as pd
import openai
import exceptions
import json
import re

load_dotenv()
API_KEY = os.getenv("API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")


def removeAll(list, remover):
    while remover in list:
        list.remove(remover)
    return list


class Bill:
    base_url = "https://api.congress.gov/v3/bill"
    apikey_header = f"api_key={API_KEY}"
    _title = None
    _titles = []
    _textURL = ""
    _text = ""
    _summary = ""

    def __init__(self, congress, billType, number):
        data = requests.get(f"{self.base_url}/{congress}/{billType}/{number}?{self.apikey_header}").json()
        if not data.get('bill'):
            raise exceptions.NoBill("Bill does not exist")
        self.raw = data['bill']


    @classmethod
    def getTextOnly(cls, congress, billType, number):
        data = requests.get(f"{cls.base_url}/{congress}/{billType}/{number}/text?{cls.apikey_header}").json()
        if data.get('error'):
            raise Exception(data['error']['message'])
        if data.get('textVersions'):
            for format in data['textVersions'][0]['formats']:
                if format['type'] == "Formatted Text":
                    print(format['url'])
                    textList = requests.get(format['url']).text.splitlines()
                    textList = removeAll([item.strip() for item in textList], "")
                    index = 11
                    text = ""
                    for i in range(index, len(textList)-4):
                        text += " " + textList[i]
                    return text
        return None

    @property
    def titles(self):
        if not self._titles:
            titlesData = requests.get(f"{self.raw['titles']['url']}&{self.apikey_header}").json()['titles']
            for title in titlesData:
                _titles.append(title['title'])
        return self._titles


    @property
    def title(self):
        if not self._title:
            print("Updating")
            self._title = self.titles[len(self.titles)-1]
        return self._title


    @property
    def textURL(self):
        if self._textURL == "":
            if self.raw.get('textVersions'):
                self._textURL = requests.get(f"{self.raw['textVersions']['url']}&{self.apikey_header}").json()['textVersions'][0]['formats'][0]['url']
            else:
                self._textURL = None
        return self._textURL


    @property
    def text(self):
        if self._text == "":
            print("Updating")
            textURL = self.textURL
            if textURL:
                textList = requests.get(textURL).text.splitlines()
                textList = removeAll([item.strip() for item in textList], "")
                index = 11
                text = ""
                for i in range(index, len(textList)-4):
                    text += " " + textList[i]
                self._text = text
            else:
                self._text = None
        return self._text


    @staticmethod
    def cleanSummary(text):
        return re.sub('<.*?>', '', text)


    @property
    def summary(self):
        if self._summary == "":
            if bill.get('summaries'):
                summaries = requests.get(f"{bill['summaries']['url']}&{apikey_header}").json()['summaries']
                text = summaries[len(summaries)-1]['text']
                text = text.replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "").replace('<p class="MsoNormal">', "").replace("<strong", "")
                self._summary = text
            else:
                self._summary = None
        return self._summary


    def getSummary(self):
        text = self.text
        if not text:
            return "No Text Provided"
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f"Imagine you are a politican explaining bills too an educated citizen. Thoroughly summarize this bill: {text}.",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response['choices'][0]['text']

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
    #summaries = requests.get(f"{Bill.base_url}/summaries/117/hr?{Bill.apikey_header}").json()

def fineTuneTexts():
    bigBills = []
    smallBills = []

    i = 0
    with open("tuning_data_text.json") as file:
        tuning_data = json.load(file)

        for data in tuning_data:
            print(data)
            if data.get('text'):
                print('cont')
                continue

            if i == 20:
                with open("tuning_data_text.json", "w+") as textFile:
                    print("dumping")
                #    json.dump(tuning_data, textFile, indent=4)
                    i = 0
            data['text'] = Bill.getTextOnly(117, "hr", data['number'])
            i += 1



fineTuneTexts()


# bills = getAllBills(117, "hr")
# for billNum in bills:
# bill = getBill(117, "hr", 2379)
# print(f"Bill: {bill['number']}: {getTitles(bill)}")
# print("\n\n")
# print(f"Original Summary: {getCongressSummary(bill)}")
# print("\n\n")
# print(f"Summary: {getSummary(bill)}")
# print("\n\n")

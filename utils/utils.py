import re
from transformers import GPT2TokenizerFast
import toml
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")


def removeAll(list, removers: list):
    for remover in removers:
        while remover in list:
            list.remove(remover)
    return list

def replaceAll(list, remover, replacer):
    while remover in list:
        list[list.index(remover)] = replacer
    return list


def removeTags(text):
    return re.sub('<.*?>', '', text)


def removeBrackets(text):
    return re.sub("\[.*?\]", "", text)


def addPeriod(text):
    if not text.endswith("."):
        text += "."
    return text


def containsNumber(string):
    return any(char.isdgit() for char in string)


def getTokens(text, completionTokens):

    promptTokens = len(tokenizer(text)['input_ids'])
    totalTokens = promptTokens + completionTokens

    return totalTokens


def getPrice(tokens, *, model, fineTuned=False):
    base_models = {
    "davinci": 0.02,
    "curie": 0.002,
    "babbage": 0.0005,
    "ada": 0.0004
    }

    fine_tuned_models = {
    "davinci": 0.12,
    "curie": 0.012,
    "babbage": 0.0024,
    "ada": 0.0016
    }

    if fineTuned:
        models = fine_tuned_models
    else:
        models = base_models

    return models.get(model) * tokens / 1000


#Given a list of numbers, returns the average
def getAverage(data: list):
    if not data:
        return None

    sum = 0
    for d in data:
        sum += d
    sum /= len(data)
    return sum


#Converts a JSON file, such as a credentials file, to a TOML
def json_to_toml(input_file, output_file="secrets.toml"):
    with open(input_file) as json_file:
        json_text = json_file.read()

    config = {"textkey": json_text}
    toml_config = toml.dumps(config)

    with open(output_file, "w") as target:
        target.write(toml_config)


def downloadFile(download_path, output_path=None):
    if not output_path:
        output_path = download_path

    if not firebase_admin._apps:
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)

    bucket = storage.bucket("resolve-87f2f.appspot.com")

    blob = bucket.blob(download_path)
    blob.download_to_filename(output_path)

    print(f"Downloaded {download_path} and saved too: {output_path}")

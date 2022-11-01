import re
from transformers import GPT2TokenizerFast
import toml

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



def json_to_toml(input_file, output_file):
    output_file = "secrets.toml"

    with open(input_file) as json_file:
        json_text = json_file.read()

    config = {"textkey": json_text}
    toml_config = toml.dumps(config)

    with open(output_file, "w") as target:
        target.write(toml_config)

import re


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

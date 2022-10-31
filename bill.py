import requests
from dotenv import load_dotenv
import os
import openai
from utils import exceptions
from utils.utils import *
import json
import re
import shutil
from recursive_summary import recursive_summary


load_dotenv()
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")



class Bill:
    base_url = "https://api.congress.gov/v3/bill"
    apikey_header = f"api_key={CONGRESS_API_KEY}"

    types_of_sort = {
    "Relevancy": None,
    "Latest Action Taken": None,
    "Latest Update": "updateDate+desc",
    "Earliest Update": "updateDate+asc",
    }

    types_of_legislation = {
    "hr": "House Bill",
    "s": "Senate Bill",
    "hjres": "House Joint Resolution",
    "sjres": "Senate Joint Resolution",
    "hconres": "House Concurrent Resolution",
    "sconres": "Senate Concurrent Resolution",
    "hres": "House Resolution",
    "sres": "Senate Resolution"
    }

    types_of_legislation_display = {
    "House Bill": "hr",
    "Senate Bill": "s",
    "House Joint Resolution": "hjres",
    "Senate Joint Resolution": "sjres",
    "House Concurrent Resolution": "hconres",
    "Senate Concurrent Resolution": "sconres",
    "House Resolution": "hres",
    "Senate Resolution": "sres"
    }

    def __init__(self, congress, type, number):
        self.congress = congress
        self.type = type
        self.number = number


    @classmethod
    def from_dict(cls, data):
        congress = data['congress']
        type = data['type'].lower()
        number = data['number']
        bill = cls(congress, type, number)

        bill.title = data.get('title')
        bill.latestAction = data.get('latestAction')
        bill.originChamber = data.get('originChamber')

        return bill


    @classmethod
    def recentBills(cls, congress, type, **kwargs):
        data = requests.get(f"{cls.base_url}/{congress}/{type}?{cls.apikey_header}&limit={kwargs.get('limit', 20)}&offset={kwargs.get('offset', 0)}&sort={kwargs.get('sort', None)}").json()
        recentBills = data.get('bills')

        if data.get('error'):
            raise Exception(data['error'])

        bills = [Bill.from_dict(bill) for bill in recentBills]
        return bills


    def getInfo(self):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}?{self.apikey_header}").json()
        bill = data.get('bill')

        if not bill:
            raise exceptions.NoBill(f"Bill {self.type.upper()} {self.number} does not exist")

        self.introducedDate = bill.get('introducedDate')
        self.sponsors = bill.get('sponsors')
        self.title = bill.get('title')
        self.policyArea = bill.get('policyArea')
        self.laws = bill.get('laws')
        self.cboCostEstimates = bill.get('cboCostEstimates')
        self.committeeReports = bill.get('committeeReports')
        self.constitutionalAuthorityStatementText = bill.get('constitutionalAuthorityStatementText')
        self.updateDate = bill.get('updateDate')
        self.latestAction = bill.get('latestAction')
        self.originChamber = bill.get('originChamber')

        return True


    def getTitles(self):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}/titles?{self.apikey_header}", verify=True).json()
        titles = []

        if data.get('error'):
            raise Exception(data['error'])

        for title in data['titles']:
            titles.append(title['title'])

        titles = [*set(titles)] #removes duplicates

        return titles


    @staticmethod
    def getShortestTitle(titles):
        shorttestTitle = titles[0]

        for title in titles:
            if len(title) < len(shorttestTitle):
                shorttestTitle = title

        return shorttestTitle


    def getTitle(self):
        titles = self.getTitles()

        if titles:
            shorttestTitle = self.getShortestTitle(titles)
            shorttestTitle = self.pruneText(shorttestTitle)
            return shorttestTitle

        else:
            return None


    def getTextURL(self, type="Formatted Text"):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}/text?{self.apikey_header}", verify=True).json()

        if data.get('error'):
            raise Exception(data['error'])

        if data.get('textVersions'):
            for format in data['textVersions'][0]['formats']:
                if format['type'] == type:
                    return format['url']
            else:
                raise Exception("Text is not avaiable in the requested format.")

        else:
            return None


    #Removes most non ASCII chars from text
    @staticmethod
    def pruneText(text):
        removers = ["_", "`", "''.", "&lt;DOC&gt;", "&lt;all&gt;", "&nbsp;", "$"]
        text = removeTags(text)
        text = removeBrackets(text)
        for remover in removers:
            text = text.replace(remover, "")
        text = re.sub(' +', ' ', text)
        text = text.lstrip().strip()
        return text


    #not combined with prune text as it is only used for the text of the bill
    @classmethod
    def cleanRawText(cls, textRaw):
        def getStartingIndex(textList):
            for line in textList:
                if not "An Act" in line and not "a bill" in line.lower() and not "AN ACT" in line and not "RESOLUTION" in line and not "Concurrent Resolution" in line:
                    continue
                return textList.index(line) + 1
            else:
                for line in textList:
                    if not "To" in line:
                        continue
                    return textList.index(line)
                else:
                    return 0

        def getFinishingIndex(textList):
            for i in range(len(textList) - 1, 0, -1):
                if not "Passed" in textList[i] and not "Attest" in textList[i] and not "Speaker of the House of Representatives" in textList[i] and not "Union Calendar" in textList[i]:
                    continue
                return i
            else:
                return len(textList)

        text = ""
        textList = textRaw.splitlines()
        textList = [item.strip() for item in textList]
        textList = removeAll(textList, [''])

        for section in textList:
            textList[textList.index(section)] = cls.pruneText(section)

        startingIndex = getStartingIndex(textList)
        finishingIndex = getFinishingIndex(textList)

        for i in range(startingIndex, finishingIndex):
            text += "\n" + textList[i]

        return text


    def getRawText(self):
        url = self.getTextURL()

        if url:
            rawText = requests.get(url).text

            if "JavaScript" in rawText:
                raise exceptions.RateLimited("You have been rate limited. Please try again later.")

            return rawText

        else:
            return None


    def getText(self):
        rawText = self.getRawText()

        if not rawText:
            return None

        text = self.pruneText(rawText)
        text = self.cleanRawText(text)
        return text


    def getSectionFromSubheader(self, target_subheader, sections=None):
        if not sections:
            sections = self.getSections()

        for section, content in sections.items():
            subheader = content.get('subheader')
            if subheader == target_subheader:
                return section


    def getSections(self):
        #Returns the text of the bill broken down into a Dictionary of sections, with subheaders and text

        text = self.getText()

        if not text:
            return None


        def split(delimiters, string, maxsplit=0):
            regex_pattern = '|'.join(map(re.escape, delimiters))
            return re.split(regex_pattern, string, maxsplit)

        def getFirstWord(line):
            for word in line:
                if word:
                    return word


        textList = split(["SECTION", "SEC."], text)

        sections = {}

        for section in textList:
            sectionList = section.splitlines()
            if sectionList[0] == '':
                sectionList[0] = "Introduction"

            firstLine = sectionList[0].split()
            sectionList.pop(0)


            firstWord = firstLine[0]
            firstLine.pop(0)

            sections[f'Section {firstWord}'] = {}
            sections[list(sections.keys())[-1]]['subheader'] = " ".join(firstLine)
            sections[list(sections.keys())[-1]]['text'] = " ".join(sectionList)

        return sections


    def getSummary(self):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}/summaries?{self.apikey_header}").json()
        summaries = data.get('summaries')

        if summaries:
            text = summaries[len(summaries)-1]['text']
            text = self.pruneText(text)
            return text
        else:
            return None


    def getActions(self):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}/actions?{self.apikey_header}").json()
        actions = data.get('actions')

        if data.get('error'):
            raise Exception(data['error'])

        return actions


    def getAmendments(self):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}/amendments?{self.apikey_header}").json()
        amendments = data.get('amendments')

        if data.get('error'):
            raise Exception(data['error'])

        return amendments


    def getRelatedBills(self):
        data = requests.get(f"{self.base_url}/{self.congress}/{self.type}/{self.number}/relatedBills?{self.apikey_header}").json()
        relatedBills = data.get('relatedBills')
        bills = [RelatedBill.from_dict(bill) for bill in relatedBills]

        if data.get('error'):
            raise Exception(data['error'])

        return bills


    def generateBrief(self, text=None):
        if not text:
            text = self.getText()

        if not text:
            raise Exception("Text is not avaiable for this bill")

        model = "text-davinci-002"
        beginning = "Imagine you are a smart politican explaining the following bill to an uneducated citizen by listing 3 of the most important takeaways from the following text: \n\n"
        ending = "\nList:"
        kwargs = {
            "model": "text-curie-001",
            "prompt": beginning + text + ending,
            "temperature": 0.3,
            "max_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }


        try:
            response = openai.Completion.create(**kwargs)
        except openai.error.InvalidRequestError:
            kwargs['model'] = "text-davinci-002"
            try:
                response = openai.Completion.create(**kwargs)
            except openai.error.InvalidRequestError:
                raise exceptions.TextTooLarge("Text is too large to get a brief, try fetching a summary instead")
            #    kwargs['prompt'] = beginning + self.generateSummary() + ending
            #    response = openai.Completion.create(**kwargs)

        print(response)

        choice = response['choices'][0]['text']
        if "\n" in choice:
            choiceList = choice.split("\n")
        else:
            choiceList = [choice]
        return choiceList


    def generateSummary(self, text=None):
        if not text:
            text = self.getText()

        if not text:
            raise Exception("Text is not avaiable for this bill.")

        beginning = "Imagine you are a smart politician tasked with explaining the following bill in a concice 100 word paragraph to an uneducated citizen: \n\n"
        ending = "\n\nSummary:"
        fullPrompt = beginning + text + ending
        price = 0
        kwargs = {
            "prompt": fullPrompt,
            "temperature": 0.25,
            "max_tokens": 512,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": ["\n"]
        }
        tokens = getTokens(text, kwargs['max_tokens'])

        if tokens <= 2049:
            kwargs["model"] = "curie:ft-personal-2022-10-23-09-13-31"
            price += getPrice(tokens, model="curie", fineTuned=True)
        elif tokens >= 2049 and tokens <= 4097:
            kwargs['model'] = "text-davinci-002"
            del kwargs['stop']
            price += getPrice(tokens, model="davinci", fineTuned=False)

        else:
            sections = self.getSections()

            if len(list(sections.keys())) > 10:
                raise exceptions.TextTooLarge("Text is too large to summarize")

            beginning = "Write a concise 20 word summary of the following bill: \n\n"
            kwargs['model'] = "text-curie-001"
            del kwargs['stop']
            count = 0

            for section, content in sections.items():
                count += 1

                text = content.get('text')
                if not text:
                    continue

                tokens = getTokens(text, kwargs['max_tokens'])
                price += getPrice(tokens, model="curie", fineTuned=False)

                kwargs['prompt'] = beginning + text + ending
                summary = recursive_summary.gpt3_completion(**kwargs)
                print('\n\n\n', count, 'of', len(sections.keys()), ' - ', summary)
                result.append(summary)

            response = '\n\n'.join(result)
            return response

        response = openai.Completion.create(**kwargs)

        # try:
        #     response = openai.Completion.create(**kwargs)
        # except openai.error.InvalidRequestError:
        #     raise Exception()
        #     tuned = False
        #     try:
        #         kwargs['model'] = "text-davinci-002"
        #         #kwargs['max_tokens'] = int(kwargs['max_tokens'] / 2)
        #         response = openai.Completion.create(**kwargs)
        #     except openai.error.InvalidRequestError:
        #         beginning = "Write a concise 20 word summary of the following bill: \n\n"
        #         kwargs['model'] = "text-curie-001"
        #         del kwargs['stop']
        #         count = 0
        #         sections = self.getSections()
        #         if len(list(sections.keys())) > 10:
        #             raise exceptions.TextTooLarge("Due to API rate limits, this text is too large to be summarized.")
        #
        #         for section, content in sections.items():
        #             count += 1
        #
        #             text = content.get('text')
        #             if not text:
        #                 continue
        #
        #             kwargs['prompt'] = beginning + text + ending
        #             summary = recursive_summary.gpt3_completion(**kwargs)
        #             print('\n\n\n', count, 'of', len(sections.keys()), ' - ', summary)
        #             result.append(summary)
        #
        #         response = '\n\n'.join(result)
        #         return response, tuned
        print(response)

        response = response['choices'][0]['text']

        response = self.pruneText(response)

        print("Price", price)
        return response



class RelatedBill(Bill):
    @classmethod
    def from_dict(cls, data):
        bill = cls.from_dict(data)
        bill.relationshipDetails = data['relationshipDetails']

if __name__ == "__main__":
    with open("output", "w+") as file:
        bill = Bill(117, "hr", 9087)
        json.dump(bill.getSections(), file, indent=4)

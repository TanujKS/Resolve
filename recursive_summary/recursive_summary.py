import openai
import os
import time
from time import sleep
import textwrap
import re
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def gpt3_completion(**kwargs):
    print("\n\nTrying chunk")
    response = openai.Completion.create(**kwargs)
    text = response['choices'][0]['text'].strip()
    text = re.sub('\s+', ' ', text)
    print("Response", text)
    filename = f'{time.time()}_gpt3.txt'
    with open(f'recursive_summary/gpt3_logs/{filename}', 'w+') as outfile:
        outfile.write('PROMPT:\n\n' + kwargs.get('prompt') + '\n\n==========\n\nRESPONSE:\n\n' + text)
    return text


def summarize(beginning, text, ending, **kwargs):
    #alltext = open_file('input.txt')
    chunks = textwrap.wrap(text, 15000)
    result = list()
    count = 0
    for chunk in chunks:
        count = count + 1
        kwargs['prompt'] = beginning + chunk + ending
        summary = gpt3_completion(**kwargs)
        print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
        result.append(summary)
    return ('\n\n'.join(result), 'output_%s.txt' % time.time())

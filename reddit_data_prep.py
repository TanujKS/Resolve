import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
base_headers = {'user-agent': 'Windows PC:resolve:v1.0.0 (by /u/awesome225007)'}
folder = "reddit_data"
newAuth = False


def getAuthToken():
    auth = requests.auth.HTTPBasicAuth('oucOYb84R-BjyxsOP2quSw', 'RUU_LRK02wdElbhX93rOUpEjqA7-kQ')

    data = {'grant_type': 'password',
            'username': 'awesome22507',
            'password': 'doglover@cool'}


    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=base_headers)

    TOKEN = res.json()['access_token']
    print(TOKEN)
    return TOKEN


def writeAuthToken(token):
    with open(".env", "a") as file:
        file.write("\n")
        file.write(f"REDDIT_API_KEY = {token}")


def df_from_response(data_list, res):
    # loop through each post pulled from res and append to df
    count = 0
    for post in res['data']['children']:
        data_list.append({
            'title': post['data']['title'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            "id": post['data']['id'],
            'created_utc': datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'kind': post['kind'],
            })
        count += 1
    return data_list, count


def fetchData(total, newAuth=False):
    print("New Auth:", newAuth)
    if newAuth:
        token = getAuthToken()
        writeAuthToken(token)
    else:
        token = os.environ.get("REDDIT_API_KEY")
        print(token)

    headers = {**base_headers, **{'Authorization': f"bearer {token}"}}
    params = {"limit": "100", "t": "all"}
    data_list = []
    totalIters = int(total/100)

    for i in range(totalIters):
        # make request
        res = requests.get("https://oauth.reddit.com/r/Politics/top", headers=headers, params=params)
        #print(res.text)
        res = res.json()


        data_list, count = df_from_response(data_list, res)
        row = data_list[len(data_list)-1]


        fullname = row['kind'] + '_' + row['id']

        params['after'] = fullname

        print(f"Added {count} entries")
        print(f"Total Entries: {len(data_list)} entries")
        print("\n")

    print("Total Entries:", len(data_list))

    df = pd.DataFrame.from_records(data_list)

    print(df.head())

    with open(f"{folder}/data.json", "w+") as file:
        file.write(df.to_json())


# def getRoundedScores(scores_list):
#     for i in range(0, len(scores_list)):
#         scores_list[i] = round(scores_list[i], (len(str(scores_list[i])) - 1) * -1)
#         scores_list[i] *=  10**-5
#         scores_list[i] = round(scores_list[i], 2)
#
#     return scores_list
#
def createSigScores():
    df = pd.read_json(f"{folder}/data.json")

    scores = df['score'].to_list()
    bottom_percentile = np.percentile(scores, 20)
    print(bottom_percentile)

    for i in range(len(scores)):
        score = scores[i]

        if score >= bottom_percentile:
            scores[i]= 1
        else:
            scores[i] = 0

    df['sig_scores'] = scores

    print(df.head())

    with open(f"{folder}/data.json", "w+") as file:
        file.write(df.to_json())


def main():
    fetchData(5000)
    createSigScores()


if __name__ == "__main__":
    main()

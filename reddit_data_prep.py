import requests
import json
import pandas as pd
from datetime import datetime

TOKEN = "22807205091-m7Rf7j-_hrYmIASFbyO_1piKV0ewEg"
base_headers = {'user-agent': 'Apple macOS:resolve:v1.0.0 (by /u/awesome225007)'}
folder = "reddit_data"

def getAuthToken():
    auth = requests.auth.HTTPBasicAuth('oucOYb84R-BjyxsOP2quSw', 'RUU_LRK02wdElbhX93rOUpEjqA7-kQ')

    data = {'grant_type': 'password',
            'username': 'awesome22507',
            'password': 'doglover@cool'}


    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)

    TOKEN = res.json()['access_token']
    print(TOKEN)
    return TOKEN


def df_from_response(data_list, res):
    # loop through each post pulled from res and append to df
    count = 0
    for post in res.json()['data']['children']:
        data_list.append({
            'title': post['data']['title'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            "id": post['data']['id'],
            'created_utc': datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'kind': post['kind']
            })
        count += 1
    return data_list, count


def fetchData(total):
    headers = {**base_headers, **{'Authorization': f"bearer {TOKEN}"}}
    params = {"limit": "100", "t": "year"}
    data_list = []
    for i in range(int(total/100)):
        # make request
        res = requests.get("https://oauth.reddit.com/r/Politics/top", headers=headers, params=params)

        data_list, count = df_from_response(data_list, res)
        print(f"Added {count} entries")
        print(f"Total: {len(data_list)} entries")
        row = data_list[len(data_list)-1]

        fullname = row['kind'] + '_' + row['id']

        params['after'] = fullname

    print("Total Entries:", len(data_list))
    data = pd.DataFrame.from_records(data_list)
    print(data.head())

    with open(f"{folder}/data.json", "w+") as file:
        file.write(data.to_json())


if __name__ == "__main__":
    fetchData(1000)

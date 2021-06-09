# This extract_text function reads tweet files that were collected
# in the past wait_next seconds, extracts text from the tweet objects
# and saves into a csv file

import os
import pandas as pd
import json
from datetime import datetime
import time
from DynamicMonitorBackend import init_pipeline

def list_files(path, pattern):

    file_list = [x for x in os.listdir(path) if pattern in x]
    file_list.sort()
    return(file_list)

def get_text(obj):

    out = None
    if 'retweeted_status' in obj:
            if 'extended_tweet' in obj['retweeted_status']:
                out = obj['retweeted_status']['extended_tweet']['full_text']
            else:
                if 'full_text' in obj['retweeted_status']:
                    out = obj['retweeted_status']['full_text']
                else:
                    out = obj['retweeted_status']['text']
    else:
        if 'extended_tweet' in obj:
            out = obj['extended_tweet']['full_text']
        else:
            if 'full_text' in obj:
                out = obj['full_text']
            else:
                out = obj['text']
    if 'quoted_status' in obj:
            if 'extended_tweet' in obj['quoted_status']:
                out = out + ' ' + obj['quoted_status']['extended_tweet']['full_text']
            else:
                if 'full_text' in obj['quoted_status']:
                    out = out + ' ' + obj['quoted_status']['full_text']
                else:
                    out = out + ' ' + obj['quoted_status']['text']
    return out.replace('\n', ' ')


def process_one_file(source_path, file_name):

    with open(source_path + file_name, 'r') as file:
        file_content = file.read()
        tweet_list = json.loads(file_content)
        file_content = None
    output = pd.DataFrame([[[],[],[]]]*len(tweet_list),
                          columns = ['id', 'created_at', 'text'])
    for i, tweet in enumerate(tweet_list):
        output['id'][i] = tweet['id']
        output['created_at'][i] = tweet['created_at']
        output['text'][i] = get_text(tweet)
    return(output)


def extract_text(source_path, output_path, pattern,
                 wait_next, marker = None):

    while True:
        # list files
        file_list = list_files(source_path, pattern)
        if marker is not None and marker in file_list:
            file_list = file_list[(file_list.index(marker) + 1):]

        # extract text
        output = pd.DataFrame(columns = ['id', 'created_at', 'text'])
        for file_name in file_list:
            result = process_one_file(source_path, file_name)
            output = output.append(result, ignore_index=True)
            marker = file_name

        # save csv
        time_now = datetime.now()
        str_format = '%Y-%m-%d-%H-%M-%S'
        output_name = 'text-{}.csv'.format(datetime.strftime(time_now, format = str_format))
        output.to_csv(output_path + output_name, index = False)
        print(output_name + ' is saved.')

        # starting backend modelling process
        monitor_time_step = '{}'.format(datetime.strftime(time_now, format = str_format))
        init_pipeline(output_name, monitor_time_step)


        # wait for the next run
        print('Waiting for the next run...')
        time.sleep(wait_next)

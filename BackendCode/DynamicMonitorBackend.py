''' Author: Maya Srikanth
This is an intermediate backend script for the data vis platform. It pulls
new twitter data, preprocesses it, runs gloves, runs visualizations, and
commits new datafiles to the repo which hosts the frontend for the platform.
'''
from git import Repo
import os
import subprocess
from preprocess_efficient import *
from word_dist import *
import argparse
import pandas as pd
import datetime

''' USER-DEFINED VARIABLES.
- repo_dir: directory of user's remote Github repository containing all dynamic monitor data.
- glove_path: path to "glove/" directory.
- working_dir: path to directory that stores all .csv outputs from word_dist.py
and time_series.py (tsne plots, arima forecast plots, raw counts plots)
 '''

data_repo_dir = 'github_username/DynamicMonitor/'
glove_path = 'glove/'

working_dir = './dynamic-computations/data/'

''' SCRIPT-DEFINED VARIABLES.
- monitor_time_step: datetime timestep indexing latest monitor files/visualizations,
updated by extract_text.py.
- keyword_list: list of keywords, pull automatically from remote repo.
- github_token: user github token to enable autmatic updating of github repo.
'''
monitor_time_step = ''
token = ''
keyword_list = []

def init_pipeline(datafile, time_step, keywords):
    '''Preprocesses new data, runs glove, creates visuals, updates
    frontend of UI. '''

    # Pull updated keywords from remote repo
    update_keyword_list() # Update keywords list
    monitor_time_step = time_step # Update timestep for file indexing

    token = os.getenv('GITHUB_PAT', '...')
    infile_name = preprocess_data(datafile)  # Preprocess Data

    run_glove(infile_name) # Run GloVe
    create_visuals()

def get_day_counts(infile_name):
    '''Obtain daily counts of keywords. Output sent for arima modelling. '''
    df = pd.read_csv(infile_name)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at',ascending=True)
    for keyword in keyword_list:
        print('Extracting daily counts for' + keyword)
        df_temp = df[df.text.str.contains(keyword)]
        df_temp = df_temp.groupby([pd.Grouper(key='created_at',freq='D')]).size().reset_index(name='Count')
        if '#' in keyword:
            fname = 'hash_' + keyword[1:] + '_' + str(monitor_time_step) + '_daycounts.csv'
        else:
            fname = keyword + '_' + str(monitor_time_step) + '_daycounts.csv'
        df_temp.to_csv(glove_dir + '/data/' + fname)


def get_hourly_counts(infile_name):
    ''' Obtain hourly counts of keywords. Output sent for arima modelling.'''
    df = pd.read_csv(infile_name)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at',ascending=True)
    for keyword in keyword_list:
        print('Extracting hourly counts for ' + keyword)
        df_temp = df[df.text.str.contains(keyword)]
        df_temp = df_temp.groupby([pd.Grouper(key='created_at',freq='H')]).size().reset_index(name='Count')
        if '#' in keyword:
            fname = 'hash_' + keyword[1:] + '_' + str(monitor_time_step) + '_hourcounts.csv'
        else:
            fname = keyword + '_' + str(monitor_time_step) + '_hourcounts.csv'
        df_temp.to_csv(glove_dir + '/data/' + fname)


def preprocess_data(infile_name):
    '''Call preprocess_efficient function on new data and output to a
    known file name (suffix=_pp), indexed by timestep.'''
    comps = infile_name.split('.')
    outfile_name = ''.join(comps[0]) + "_pp.csv"
    preprocess(infile_name, outfile_name)
    return outfile_name

def run_glove(infile_name): # TESTED
    ''' Set the CORPUS environment variable and initiates GloVe training
    on preprocessed data by calling glove/demo.sh.'''
    #corpus_name = '/mnt/vol2/glove/' + infile_name
    corpus_name = glove_path + infile_name
    os.putenv("CORPUS", corpus_name)
    subprocess.call(['sh', './demo.sh'])

def update_keyword_list():
    '''Pull latest keywords from remote repo and updates global var
    accordingly.'''
    g = Github(token)
    repo = g.get_repo(repo_dir)
    file_path = "data/LatestKeywords.csv"
    file = repo.get_contents(file_path, ref="main")  # Get file from main branch
    data = file.decoded_content.decode("utf-8")  # Get raw string data
    temp = data.split('\n')
    temp.pop(0) # popping header
    for el in temp:
        if el != '':
            kw_el = el.split(',')[1] # grab keyword
            keyword_list.append(kw_el) # update global var


def create_visuals():
    '''Runs the visualization code from word_dist.py and saves the new info
    to .csv files. Updates remote repository data/ directory to show these files. '''

    # Check for dynamic-computations/data directory and create if not there.
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    get_tsne_visuals(keyword_list, 30, monitor_time_step)
    # TODO: Add timestep to last row of LatestKeywords.csv & push changes.

    g = Github(token)
    repo = g.get_repo(data_repo_dir)

    for keyword in keyword_list: #f"{path}{keyword}_tsne{tsne_time_step}.csv"
        keyword_fm = keyword
        if '#' in keyword:
            keyword_fm = 'hash_' + keyword[1:]

        filepath_tsne = "./dynamic-computations/data/" + keyword_fm + "_tsne" + monitor_time_step + ".csv"
        if os.path.exists(fname_tsne):
            git_file_path = 'data/' + keyword_fm + '_tsne' + monitor_time_step + '.csv'
            with open(filepath_tsne, 'r') as file:
                content = file.read()
            repo.create_file(git_file_path, "committing tsne", content, branch="main")
            print(git_file_path + ' CREATED')


def push_files(file_list):
    ''' FUNCTION NO LONGER IN USE. System now relies on personal access token
    for github. '''
    repo = Repo(repo_dir)
    commit_message = 'Pushing updated data files for dynamic monitor.'
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.push()


if __name__ == '__main__':
    print("STARTING...\n\n")
    init_pipeline('twitter-election-dynamic-day5.csv')

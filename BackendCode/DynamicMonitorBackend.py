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

''' USER-DEFINED VARIABLES: (see below)
- repo_dir: directory of user's github.io repository
- keyword_list: list of keywords, updated by launch_monitor.py.
- glove_dir: path to "glove/" directory.
- github_token: user github token to enable autmatic updating of github repo.
 '''
repo_dir = 'username.github.io/'
keyword_list = ['#boston', '#bostonbombings', '#bostonmarathon', '#marathonday', \
'#cambridge']
glove_dir = 'glove/'
github_token = ''

''' SCRIPT-DEFINED VARIABLES
- monitor_time_step: datetime timestep indexing latest monitor files/visualizations,
updated by extract_text.py.
'''
monitor_time_step = 1

def init_pipeline(datafile):
    '''Preprocesses new data, runs glove, creates visuals, updates
    frontend of UI. '''
    infile_name = preprocess_data(datafile)  # Preprocess Data
    update_keyword_list() # Update keywords list
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
    '''Helper function for updating keywords list file. '''
    final_ls = []
    for keyword in keyword_list:
        if '#' in keyword:
            final_ls.append('hash_' + keyword[1:])
        else:
            final_ls.append(keyword)
    fname = repo_dir + 'data/LatestKeywords.csv'
    df = pd.DataFrame({'Keywords': final_ls})
    df.to_csv(fname)

def create_visuals():
    # in process of fixing this to make it work with user-defined credentials
    '''Runs the visualization code from word_dist.py and saves the new info
    to .csv files.'''
    get_tsne_visuals(keyword_list, 30, tsne_time_step)
    file_list = []
    path = repo_dir + 'data/'
    for keyword in keyword_list: #fname = f"{path}{keyword}_tsne{tsne_time_step}.csv"
        if '#' in keyword:
            keyword = 'hash_' + keyword[1:]
        name = path + keyword + "_tsne" + str(tsne_time_step) + ".csv"
        file_list.append(name)

    push_files(file_list)


# Running this in parent directory of repository... TESTED!
def push_files(file_list):
    repo = Repo(repo_dir)
    commit_message = 'Pushing updated data files for dynamic monitor.'
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.push()


if __name__ == '__main__':
    print("STARTING...\n\n")
    init_pipeline('twitter-election-dynamic-day5.csv')

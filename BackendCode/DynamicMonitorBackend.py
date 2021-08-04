''' Author: Maya Srikanth
This is an intermediate backend script for the data vis platform. It pulls
new twitter data, preprocesses it, runs gloves, runs visualizations, and
commits new datafiles to the repo which hosts the frontend for the platform.
'''

from github import Github
import os

import subprocess
from preprocess_efficient import *
from word_dist import *

import pandas as pd
import datetime
from time_series_model import *



''' USER-DEFINED VARIABLES.
- repo_dir: directory of user's remote Github repository containing all dynamic monitor data.
- glove_path: path to "glove/" directory.
- working_dir: path to directory that stores all .csv outputs from word_dist.py
and time_series.py (tsne plots, arima forecast plots)
 '''
repo_dir = 'mayasrikanth/mayasrikanth.github.io'
glove_path = 'GloVe-master/'
working_dir = 'DynamicDataOutput/'

''' SCRIPT-DEFINED VARIABLES.
- monitor_time_step: datetime timestep indexing latest monitor files/visualizations,
updated by extract_text.py.
- keyword_list: list of keywords, pull automatically from remote repo.
- github_token: user github token to enable autmatic updating of github repo.
'''
monitor_time_step = ''
token = ''

def init_pipeline(datafile, time_step):
    '''Preprocesses new data, runs glove, creates visuals, updates
    frontend of UI. '''
    token = os.getenv('GITHUB_PAT', '...')
    # ensure working directory which holds all intermediate .csv files exists
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    # Pull updated keywords from remote repo
    keyword_list = update_keyword_list(token) # Update keywords list
    print("current keywords: ", keyword_list)
    monitor_time_step = time_step # Update timestep for file indexing

    get_day_counts(datafile, keyword_list, time_step) # run arima on day counts
    get_hourly_counts(datafile, keyword_list, time_step) # run arima on hour counts

    infile_name = preprocess_data(datafile)  # Preprocess Data
    glove_path = 'GloVe-master/'
    run_glove(infile_name, glove_path) # Run GloVe
    create_visuals(keyword_list, token, monitor_time_step)


def get_day_counts(infile_name, keyword_list, time_step):
    '''Obtain daily counts of keywords. Intermediate raw counts .csv output to
       working directory. Filepath of this output is sent to time_series_model.py
       for arima modelling.'''
    df = pd.read_csv(infile_name)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at',ascending=True)
    # set datetime index
    df.index = df.set_index('created_at')
    df.dropna() # drop nan rows

    for keyword in keyword_list:
        print('Extracting daily counts for ' + keyword)
        df_temp = df.loc[df.text.str.contains(keyword, na=False)]

        if df_temp.empty:
            continue # do not proceed with time series analysis.

        df_temp = df_temp.groupby([pd.Grouper(key='created_at',freq='D')]).size().reset_index(name='Count')
        # fill in missing days with 0
        df_temp.dropna()
        df_temp.index = df_temp['created_at']
        # Reset index & fill missing hours with counts=0
        idx = pd.date_range(df_temp['created_at'].min(), df_temp['created_at'].max(), freq='D')
        df_temp = df_temp.reindex(idx, fill_value=0)
        if '#' in keyword:
            fname = 'hash_' + keyword[1:] + '_' + str(time_step) + '_daycounts.csv'
        else:
            fname = keyword + '_' + str(time_step) + '_daycounts.csv'

        # Call time series modelling
        fname_res = working_dir + fname
        print("FILE PATH DAILY COUNTS: ", fname_res)
        df_temp.to_csv(fname_res)
        time_series_model(fname_res, monitor_time_step, keyword, working_dir)


def get_hourly_counts(infile_name, keyword_list, time_step):
    ''' Obtain hourly counts of keywords. Output sent for arima modelling.'''
    df = pd.read_csv(infile_name)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at',ascending=True)
    # set datetime index
    df.index = df.set_index('created_at')
    df.dropna()

    for keyword in keyword_list:
        print('Extracting hourly counts for ' + keyword)
        df_temp = df.loc[[df.text.str.contains(keyword, na=False)]]
        if df_temp.empty:
            continue # do not proceed with time series analysis.
        df_temp = df_temp.groupby([pd.Grouper(key='created_at',freq='H')]).size().reset_index(name='Count')
        df_temp.index = df_temp['created_at']
        # Reset index & fill missing hours with counts=0
        idx = pd.date_range(df_temp['created_at'].min(), df_temp['created_at'].max(), freq='H')
        df_temp = df_temp.reindex(idx, fill_value=0)

        if '#' in keyword:
            fname = 'hash_' + keyword[1:] + '_' + str(time_step) + '_hourcounts.csv'
        else:
            fname = keyword + '_' + str(time_step) + '_hourcounts.csv'

        # Call time series modelling function with filename
        fname_res = working_dir + fname
        df_temp.to_csv(fname_res)
        time_series_model(fname_res, monitor_time_step, keyword, working_dir)


def preprocess_data(infile_name):
    '''Call preprocess_efficient function on new data and output to a
    known file name (suffix=_pp), indexed by timestep.'''
    comps = infile_name.split('.')
    outfile_name = ''.join(comps[0]) + "_pp.csv"
    preprocess(infile_name, outfile_name)
    return outfile_name

def run_glove(infile_name, glove_path): # tested
    ''' Set the CORPUS environment variable and initiates GloVe training
    on preprocessed data by calling glove/demo.sh.'''
    #corpus_name = '/mnt/vol2/glove/' + infile_name
    cwd = os.getcwd()
    corpus_name = cwd + '/' + infile_name
    print('CORPUS NAME: ', corpus_name)
    os.putenv("CORPUS", corpus_name)
    os.chdir(glove_path)
    subprocess.call(['sh', './demo.sh'])
    os.chdir(cwd)
    print("Current directory: ", cwd)

def update_keyword_list(token):
    '''Pull latest keywords from remote repo and updates global var
    accordingly.'''
    g = Github(token)
    repo = g.get_repo(repo_dir)
    file_path = "data/LatestKeywords.csv"
    file = repo.get_contents(file_path, ref="main")  # Get file from main branch
    data = file.decoded_content.decode("utf-8")  # Get raw string data
    temp = data.split('\n')
    temp.pop(0) # popping header
    temp.pop() # popping date time
    temp.pop()
    keyword_list = []
    for el in temp:
        if el != '':
            kw_el = el.split(',')[2] # grab keyword
            print(kw_el)
            kw_el = kw_el.replace('hash_', '#')
            print(kw_el)
            keyword_list.append(kw_el) # update global var
    print("keywords: ", keyword_list)
    return keyword_list

def create_visuals(keyword_list, token, monitor_time_step):
    '''Runs the visualization code from word_dist.py and saves the new info
    to .csv files. Updates remote repository data/ directory to show these files. '''
    g = Github(token)
    repo = g.get_repo(repo_dir)
    file = repo.get_contents('data/LatestKeywords.csv', ref="main")

    # Check for dynamic-computations/data directory and create if not there.
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    get_tsne_visuals(keyword_list, 30, monitor_time_step)

    # Update last row of LatestKeywords.csv with timestep & push changes.
    git_raw_prefix = 'https://raw.githubusercontent.com/'
    branch_name = 'main'
    git_file_path = git_raw_prefix + repo_dir + '/' + branch_name + '/data/LatestKeywords.csv'
    df = pd.read_csv(git_file_path, error_bad_lines=False)

    monitor_time_step = monitor_time_step.replace(' ', '_')
    temp = df.Keywords.values
    # assuming timestep is last element
    temp[len(temp)-1] = monitor_time_step
    # Save back into df
    df.Keywords = temp
    df.to_csv(working_dir + 'LatestKeywords.csv')

    keywords_path = working_dir + 'LatestKeywords.csv'
    with open(keywords_path, 'r') as file:
        content = file.read()

    contents = repo.get_contents('data/LatestKeywords.csv', ref='main')  # grab contents of file
    repo.update_file(contents.path, message, content, contents.sha, branch='main')

    for keyword in keyword_list: #f"{path}{keyword}_tsne{tsne_time_step}.csv"
        keyword_fm = keyword
        if '#' in keyword:
            keyword_fm = 'hash_' + keyword[1:]
        filepath_tsne = working_dir + keyword_fm + "_tsne" + monitor_time_step + ".csv"
        if os.path.exists(fname_tsne): # if visual was created
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
    time_step = '2021-01-12-21-26-10'
    #run_glove('StreamedData/twitter-election-dynamic-day7_pp.csv', 'GloVe-master/')
    init_pipeline('StreamedData/bostonref.csv', time_step)

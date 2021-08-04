''' time_series_model.py should be in same directory as DynamicMonitorBackend.py

A fun link for some theory behind arima: https://otexts.com/fpp2/stationarity.html
The general breakdown of tasks this script does:
1. Parse twitter time series data, split into test / train
2. Log Transform
3. Choose best fit with python auto_arima
4. Use model to project 10 timesteps into future.
5. Output results to .csv file, index with correct timestep
6. Push changed files to github remote repo.
REPEAT for each keyword.

'''

import pandas as pd
from github import Github
import os
import numpy as np

from pmdarima.pipeline import Pipeline
from pmdarima.preprocessing import LogEndogTransformer

import pmdarima as pm
from pmdarima.arima import StepwiseContext, AutoARIMA

'''
data_repo_dir: this is the path to your remote Github repository which
holds the data folder containing dynamic monitor visualizations.New files
will be pushed to this remote location.
'''
data_repo_dir = 'mayasrikanth/mayasrikanth.github.io/'


def time_series_model(fname, monitor_time_step, keyword, output_dir):
    df = pd.read_csv(fname)
    data = df.Count.values

    # split into train and test (actually not necessary)
    test_idx = int(len(data) * 0.75)
    train, test = data[:test_idx], data[test_idx:]

    # create preprocessing & training pipeline
    pipeline = Pipeline([
    ("log", LogEndogTransformer()),
    ("arima", AutoARIMA(seasonal=False, stepwise=True,
                        start_p=1, start_q=1,
                        #max_p=5, max_q=5
                        suppress_warnings=True,
                        error_action='ignore'))
                        ])

    # fit stepwise auto-ARIMA
    pipeline.fit(data)

    # forecast 10 steps into future & obtain projection conf intervals
    preds, conf_int = pipeline.predict(n_periods=10, return_conf_int=True)
    print("\nForecasts:")
    print(preds)

    # generate .csv file with conf_low, conf_area, and series
    padding = np.zeros(len(data))
    conf_low = np.concatenate((data, conf_int[:,0]))
    conf_high = np.concatenate((padding, conf_int[:,1]))
    conf_area = np.concatenate((padding, conf_int[:,0] + conf_int[:,1]))

    # Note that inverse of log is automatically applied.
    freq = np.concatenate((data, preds))

    df_output = pd.DataFrame({'freq': freq, 'conf_low':conf_low, \
                              'conf_area': conf_area})

    output_fpath = output_dir + keyword + "_" + str(monitor_time_step) + "_forecast.csv"
    df_output.to_csv(output_fpath)

    # call update_remote_repo to push this file to your remote data directory
    update_remote_repo(output_fpath, keyword, monitor_time_step)



def update_remote_repo(output_fpath, keyword, monitor_time_step):
        token = os.getenv('GITHUB_PAT', '...')
        g = Github(token)
        repo = g.get_repo(data_repo_dir)

        # Pushing file to github
        with open(output_fpath, 'r') as file: # reading new .csv containing forecasts
            content = file.read()

        monitor_time_step = monitor_time_step.replace(' ', '_')
        git_file_path = 'data/' + keyword + '_' + monitor_time_step + '_forecast.csv'
        repo.create_file(git_file_path, "committing updated time series", \
                        content, branch="main")
        print(git_file_path + ' CREATED')

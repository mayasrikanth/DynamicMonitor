# DynamicMonitor 🌍

This repository contains code for a semi-automated and dynamic social media data collection process. We presented a [short paper](https://arxiv.org/abs/1911.05332) containing preliminary analyses at NeurIPS 2019 AI for Social Good Workshop in Canada which details our initial project motivation and insights. 

A few years later, we are publishing our most updated work in the 2021 ACM SIGKDD Conference Proceedings and ACM DL journal! This repository contains code pertaining to this paper. We'll include these links once the publication is finalized. 

## Collaborators
Maya Srikanth, Anqi Liu, Nicholas Adams-Cohen, Jian Cao, R. Michael Alvarez, and Anima Anandkumar. We are part of Caltech's Trustworthy Social Media group, focused on using AI and social science to study patterns in online communication and combat rampant issues like misinformation and online abuse. 

Here is a quick breakdown of key scripts/components in this repo. 

## Backend Overview
- **DynamicMonitorBackend.py**: initiates training GloVe word embeddings, producing visualizations, running time series models, and finally updating the github repository storing all dynamic monitor data to reflect the newest keyword information.
- **launch_monitor.py**: starts monitor which uses user-provided keywords to collect data from Twitter streaming API, saves collected tweets into local .txt files.
- **preprocess_efficient.py**: uses parallel processing with dask to preprocess textual Tweet data, output used to train GloVe embeddings.
- **sample_run_py**: example code for starting the twitter monitor, and thus the prcess of dynamic keyword selection
- **GloVe implementation**: we retrain GloVe embeddings from scratch on real-time social media data. Because the official GloVe repo publicly available, we do not include it here.
- **extract_text.py**: at set time intervals, this script extracts necessary datetime and content information from collected tweets, saves this into a .csv file, and calls upon DynamicMonitorBackend.py to start the process of NLP modelling on the latest batch of twitter data.
- **word_dist.py**: script for finding closest neighbors to a given keyword and populating .csv file with this information.
- **time_series.py**: basic script for time series modelling with ARIMA (including data preprocessing, parameter tuning, and projecting 15 timesteps into future). If a good fit is not found, the final script will revert to rolling average predictions. Note that I am in the process of rewriting this script.


## Frontend Overview (UPDATE THIS FOLDER WITH LATEST UI)
- **web_platform** folder contains javascript and html files used for the frontend of our data visualization platform. 

Here is a link to a demo of the frontend UI we used for studying the 2021  [presidential #inauguration](https://mayasrikanth.github.io/social-media-trends/)
on Twitter (featured in our paper). I recently renovated the UI and added more dynamic components: [here's](https://mayasrikanth.github.io/dynamic-monitor-new/) an updated demo of the frontend UI for the data visualization platform we built. The latter is what your own data vis platform setup will look like once you're finished with the tutorial below. 

## Data Collection
See [Jian Cao's python package](https://github.com/jian-frank-cao/spike) for setting up Twitter data streaming and uploading this data to a database or google cloud. Our final monitor version will integrate with this package to allow for automated data streaming. 

We are actively updating our time series methods and adding more scripts/documentation to this repository. We plan to officially release code for other researchers to use in June 2021, and estimate to have most updated material up by mid-June.


## Getting Started  
### 1. Understanding platform setup 
A useful first step before starting the set up process is to understand the general workflow of scripts in the dynamic monitor repository. 

![alt text](https://github.com/mayasrikanth/DynamicMonitor/blob/main/Figures/platform-workflow.png)
### 2. Clone and create necessary repositories. 
First, clone this repository. You'll need these scripts to start the monitor. Then, clone Stanford's publicly available [GloVe repository](https://nlp.stanford.edu/projects/glove/). 

As shown in the image above, you'll need a public repository to store .csv files containing numerical data to produce visualizations and forecasting information for each keyword. You will also need a new public repository to host the frontend UI. You can very well use the same public repository to perform both tasks, or you can set up two different repositories if that better suits your organizational preferences.

### 2. Set up Github Personal Access Token
Head to your github account and generate a personal access token. To maintain security, our code uses personal access tokens to connect to the Github API and update the data necessary for frontend visualizations. Our scripts assume that your personal access token is stored in the permanent environment variable GITHUB_PAT. Accordingly, please update your os file containing all environment variables with the line:

```export GITHUB_PAT = your_personal_access_token```

### 3. Set up Twitter Developer Credentials
If you haven't already, please set up your Twitter developer credentials. This will allow you to connect to various Twitter endpoint APIs and pull tweets of interest. Once you do this, head to sample_run.py (or whatever you decide to rename it) and fill in your consumer_key, consumer_secret, access_token_key, and access_token_secret. 


### 4. Set up Data Vis Platform code (FILL IN)
  - File structure
  - User-defined variables (directories, etc)
  - Updating Keywords
  - Time interval customization 
  - Frontend updates




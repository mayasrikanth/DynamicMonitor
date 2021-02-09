# DynamicMonitor

This repository contains code for a semi-automated and dynamic social media data collection process. We presented our original paper and preliminary analyses at NeurIPS 2019 AI for Social Good Workshop in Canada. See (https://arxiv.org/abs/1911.05332) for project motivation and initial insights.

## Collaborators
Maya Srikanth, Anqi Liu, Nicholas Adams-Cohen, Jian Ciao, R. Michael Alvarez, and Anima Anandkumar. We are part of Caltech's Trustworthy Social Media group, focused on using AI and social science to study patterns in online communication and combat rampant issues like misinformation and online abuse. 

Here is a quick breakdown of key scripts/components in this repo. 

## Backend 
- GloVe implementation: we retrain GloVe embeddings from scratch on real-time social media data.
- word_dist.py: script for finding closest neighbors to a given keyword and populating .csv file with this information.
- time_series.py: basic script for time series modelling with ARIMA (including data preprocessing, parameter tuning, and projecting 15 timesteps into future)

## Frontend 
- web_platform folder contains javascript and html files used for the frontend of our data visualization platform.



We are actively updating our time series methods and adding more scripts/documentation to this repository. We plan to officially release code for other researchers to use late March 2021. 

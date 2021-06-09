# This launch_monitor function starts a Twitter monitor that uses
# user-provided keywords to collect tweets from filtered stream endpoint,
# and saves the collected tweets into local .txt files

import pip
try:
    __import__('spike')
except ImportError:
    package_spike = 'git+https://github.com/jian-frank-cao/spike.git@main'
    pip.main(['install', package_spike])


try:
    __import__('github')
except ImportError:
    pip.main(['install', 'PyGithub'])

from github import Github
from spike.TwitterMonitor import ConnectTwitterAPI
import pandas as pd


def launch_monitor(consumer_key, consumer_secret,
                   access_token_key, access_token_secret,
                   github_token, github_repo,
                   git_prefix, keywords, download_path,
                   file_prefix, minutes_per_file = 5):
    # check path
    if download_path[-1] != '/':
            download_path = download_path + '/'

    # save keywords
    keywords_path = download_path + 'LatestKeywords.csv'
    LatestKeywords = pd.DataFrame([x.replace('#','hash_') for x in keywords],
                                 columns = ['keywords'])
    LatestKeywords.to_csv(keywords_path)

    # git push LatestKeywords.csv
    g = Github(github_token)
    repo = g.get_user().get_repo(github_repo)
    all_files = []
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    with open(keywords_path, 'r') as file:
        content = file.read()

    git_file = git_prefix + 'LatestKeywords.csv'
    if git_file in all_files:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
        print(git_file + ' UPDATED')
    else:
        repo.create_file(git_file, "committing files", content, branch="main")
        print(git_file + ' CREATED')

    # connect Twitter API
    twitter_api = ConnectTwitterAPI(consumer_key,
                                    consumer_secret,
                                    access_token_key,
                                    access_token_secret)

    # start monitor
    twitter_api.StartMonitor(input_dict = {'keywords' : keywords,
                                          'download_path': download_path,
                                          'file_prefix': file_prefix,
                                          'minutes_per_file': minutes_per_file},
                            api_type = 'stream_v1',
                            outlet_type = 'local')

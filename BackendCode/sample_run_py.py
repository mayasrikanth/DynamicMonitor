# This script shows how to call the launch_monitor and
# extract_text functions

# launch monitor
import launch_monitor

keywords = ['biden']
download_path = '/DOWNLOAD PATH/'
file_prefix = 'twitter-biden'
github_repo = 'GITHUB_REPO'
git_prefix = 'GITHUB_FOLDER/'

consumer_key = ''
consumer_secret = ''
access_token_key = ''
access_token_secret = ''
github_token = ''

launch_monitor(consumer_key, consumer_secret,
			   access_token_key, access_token_secret,
			   github_token, github_repo,
			   git_prefix, keywords, 
			   download_path, file_prefix)

# extract text
import extract_text

source_path = '/SOURCE PATH/'
output_path = '/OUTPUT PATH/'
pattern = '.txt'
wait_next = 20

extract_text(source_path, output_path, pattern,
             wait_next, marker = None)


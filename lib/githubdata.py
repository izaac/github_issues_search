import datetime
import os
import pickle
import sys
from github import Github

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_DATA_TIMEOUT = 900
GH_SESSION = None


def github_authenticate(token=None):
    if GITHUB_TOKEN is None and token is None:
        print('Please set access token in environment variable GITHUB_TOKEN or use --token')
        sys.exit(1)
    global GH_SESSION
    GH_SESSION = Github(token) if token else Github(GITHUB_TOKEN)
    return GH_SESSION


def get_github_session():
    return GH_SESSION


def process_github_data(repo_data='repo.data'):
    now = datetime.datetime.now()
    if os.path.isfile(repo_data):
        repo_data_mod_time = datetime.datetime.fromtimestamp(
            os.path.getmtime(repo_data)
        )
        delete_file = now - repo_data_mod_time > datetime.timedelta(minutes=15)
        if delete_file:
            os.remove(repo_data)
    repos = None
    if not os.path.isfile(repo_data):
        print('Loading from Github')
        if GH_SESSION is None:
            g = github_authenticate()
        else:
            g = get_github_session()
        repos = g.get_user().get_repos()
        with open(repo_data, 'wb') as f:
            pickle.dump(repos, f)
    else:
        print("Loading from Cache")
        try:
            with open(repo_data, 'rb') as f:
                repos = pickle.load(f)
        except FileNotFoundError as e:
            print(e)
    return repos

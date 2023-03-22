#!/usr/bin/env python3
# Find all active github repos for the wikimedia account
import os
import re
import requests
import sys

from datetime import datetime, timezone
from time import time, sleep

pattern = re.compile(r'<(.*)>')

# Obtain from <https://github.com/settings/tokens>
#
# https://docs.github.com/en/rest/overview/authenticating-to-the-rest-api
GH_AUTH_HEADERS = {"authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ['GITHUB_TOKEN'] else None


def active_fork(repo):
    """
    TODO: forks are hard...
    """
    r = requests.get(repo['url'], headers=GH_AUTH_HEADERS)
    r.raise_for_status()
    full_repo = r.json()

    # Parent repo is archived
    parent_inactive = full_repo['parent']['archived'] == True

    # Fork is more up-to-date than the parent
    fork_updated = full_repo['updated_at']
    parent_updated = full_repo['parent']['updated_at']

    fork_more_active = fork_updated > parent_updated

    return parent_inactive or fork_more_active


def valid_repo(repo):
    """
    Filter out repos that are archived or forks.
    """
    if repo['archived']:
        return False

    # if repo['fork']:
    #     return active_fork(repo)

    # It's not archived, it's not a fork, it's a valid repo
    return True


url = 'https://api.github.com/users/wikimedia/repos?sort=pushed'
repos = []
file_name = 'github-repos-{}'.format(datetime.now(tz=timezone.utc).strftime('%Y-%m-%d'))
with open(file_name, 'w') as f:
    while url:
        r = requests.get(url, headers=GH_AUTH_HEADERS)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.reason == 'rate limit exceeded':
                raise e

            # Stop
            url = None
            continue

        f.write('\n'.join([x['full_name'] for x in r.json() if valid_repo(x)]))
        f.write('\n')

        links = r.headers['link'].split(',')
        for link in links:
            if 'next' not in link:
                continue
            uri, _ = link.split(';')

        try:
            new_url = pattern.search(uri).group(1).strip()
            if  new_url == url:
                sys.exit(0)
            url = new_url
        except AttributeError:
            url = None
            pass
        print('next: {}'.format(url))

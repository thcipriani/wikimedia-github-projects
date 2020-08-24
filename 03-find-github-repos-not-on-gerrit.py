#!/usr/bin/env python
# Find github repos that don't have corresponding gerrit repos
import os
import multiprocessing

from datetime import datetime,timezone

import requests

DATE = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')
GITHUB_URL = 'https://github.com/'
GITHUB_REPOS = 'github-repos-{}'.format(DATE)
GERRIT_REPOS = 'gerrit-repos-{}'.format(DATE)
GITHUB_UNIQUES = 'github-repos-not-on-gerrit-{}'.format(DATE)

def trim_beg(haystack, needle):
    return haystack[len(needle):]


def gerrit_to_github(reponame):
    """
    Convert gerrit name to github name
    e.g., wikimedia/mediawiki/core -> wikimedia/mediawiki-core
    """
    return os.path.join('wikimedia', reponame.strip().replace('/', '-'))


def canonical(reponame):
    """
    Make HEAD request to github

    if the status is 301, return the canonical redirect, otherwise, return the
    repo name
    """
    github_repo = GITHUB_URL + reponame
    r = requests.head(github_repo)
    print('checking "{}" - {}'.format(github_repo, r.status_code))
    if r.status_code == 301:
        return trim_beg(r.headers['location'], GITHUB_URL)
    return reponame


if __name__ == '__main__':
    gerrit_repos = set()
    with open(GITHUB_REPOS) as f:
        github_repos = set([x.strip() for x in f.readlines()])

    with open(GERRIT_REPOS) as f:
        gerrit_repos = {}
        gerrit_repos = [gerrit_to_github(x.strip()) for x in f.readlines()]

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        gerrit_repos = pool.map(canonical, gerrit_repos)

    gerrit_repos = set(gerrit_repos)

    with open(GITHUB_UNIQUES, 'w') as f:
        # remove the set of gerrit repos from the set of github repos, leaving
        # only those repos that are exclusive to github
        f.write('\n'.join(github_repos - gerrit_repos))

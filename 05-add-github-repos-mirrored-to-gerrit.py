#!/usr/bin/env python3

# Add in any repos that phabricator is *observing* on github and *mirroring* to
# gerrit

import json
import os
import requests

from datetime import datetime, timezone


DATE = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')
GITHUB_REPOS = 'active-github-repos-{}'.format(DATE)
FINAL_FILE = 'README'


def flatten_for_post(h, result=None, kk=None):
    """
    Since phab expects x-url-encoded form post data (meaning each
    individual list element is named). AND because, evidently, requests
    can't do this for me, I found a solution via stackoverflow.

    See also:
    <https://secure.phabricator.com/T12447>
    <https://stackoverflow.com/questions/26266664/requests-form-urlencoded-data/36411923>
    """
    if result is None:
        result = {}

    if isinstance(h, str) or isinstance(h, bool):
        result[kk] = h
    elif isinstance(h, list) or isinstance(h, tuple):
        for i, v1 in enumerate(h):
            flatten_for_post(v1, result, '%s[%d]' % (kk, i))
    elif isinstance(h, dict):
        for (k, v) in h.items():
            key = k if kk is None else "%s[%s]" % (kk, k)
            if isinstance(v, dict):
                for i, v1 in v.items():
                    flatten_for_post(v1, result, '%s[%s]' % (key, i))
            else:
                flatten_for_post(v, result, key)
    return result


class Phab(object):
    def __init__(self):
        self.phab_url = 'https://phabricator.wikimedia.org/api/'
        self.conduit_token = self._get_token()

    def _get_token(self):
        """
        Use the $CONDUIT_TOKEN envvar, fallback to whatever is in ~/.arcrc
        """
        token = None
        token_path = os.path.expanduser('~/.arcrc')
        if os.path.exists(token_path):
            with open(token_path) as f:
                arcrc = json.load(f)
                token = arcrc['hosts'][self.phab_url]['token']

        return os.environ.get('CONDUIT_TOKEN', token)

    def _query_phab(self, method, data):
        """
        Helper method to query phab via requests and return json
        """
        data = flatten_for_post(data)
        data['api.token'] = self.conduit_token
        r = requests.post(
            os.path.join(self.phab_url, method),
            data=data)
        r.raise_for_status()
        return r.json()

    def find_uris(self, ret, after=None):
        """
        Get a set of authors from a list of commit sha1s
        """
        data = {
                "queryKey": "all",
                "attachments": {
                    'uris': '1',
                },
            }

        if after:
            data['after'] = after

        repos = self._query_phab(
            'diffusion.repository.search',
            data
        )

        results = repos['result']

        if not results:
            return ret

        for repo in results['data']:
            observe_github = False
            mirror_gerrit = False

            for uri in repo['attachments']['uris']['uris']:
                # Looking only for uris that are pointing to gerrit
                # that are also of io type "observe"
                phid = uri['id']
                name = uri['fields']['uri']['raw']
                io  = uri['fields']['io']['raw']
                if 'https://github.com/wikimedia' in name and io == 'observe':
                    observe_github = True
                    github_name = name
                if 'gerrit.wikimedia.org' in name and io == 'mirror':
                    mirror_gerrit = True

            if observe_github and mirror_gerrit:
                repo_github_name = github_name[len('https://github.com/'):]
                print(repo_github_name)
                ret.add(repo_github_name)

        after = results['cursor']['after']
        if after:
            self.find_uris(ret, after)

        else:
            return ret

    # def update_uri(self, phid, uri):
    #     method = 'diffusion.uri.edit'
    #     data = {
    #         'objectIdentifier': str(phid),
    #         'transactions': [{
    #             'type': 'uri',
    #             'value': str(uri)
    #         }]
    #     }
    #     print(flatten_for_post(data))
    #     # return {'error_code': None}
    #     return self._query_phab(method, data)


def main():
    with open(GITHUB_REPOS) as f:
        github_repos = set(f.read().splitlines())

    github_mirrors = set()
    p = Phab()
    p.find_uris(github_mirrors)

    with open(FINAL_FILE, 'w') as f:
        f.write('\n'.join(sorted(github_mirrors | github_repos)))


if __name__ == '__main__':
    main()

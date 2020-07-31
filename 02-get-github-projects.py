#!/usr/bin/env python3
# Find all active github repos for the wikimedia account
import re
import requests
import sys

from datetime import datetime,timezone


pattern = re.compile(r'<(.*)>')


url = 'https://api.github.com/users/wikimedia/repos'
repos = []
file_name = 'github-repos-{}'.format(datetime.now(tz=timezone.utc).strftime('%Y-%m-%d'))
with open(file_name, 'w') as f:
    while url:
        r = requests.get(url, auth=())
        r.raise_for_status()
        f.write('\n'.join([x['full_name'] for x in r.json() if x['archived'] == False]))
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

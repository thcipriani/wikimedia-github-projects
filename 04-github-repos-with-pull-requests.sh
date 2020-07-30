#!/usr/bin/env bash
DATE="$(date -I)"
cat /dev/null > "active-github-repos-$DATE"
while read -r repo; do
    printf 'Checking %s...' "$repo"
    if (( $(git ls-remote https://github.com/"$repo" refs/pull/* | wc -l) > 0 )); then
        echo "$repo" >> "active-github-repos-$DATE"
    fi
    printf 'DONE!\n'
done < "github-repos-not-on-gerrit-$DATE"

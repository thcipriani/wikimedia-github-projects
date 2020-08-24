#!/usr/bin/env bash
set -euo pipefail
DATE=$(date -I)

cat /dev/null > "active-github-repos-$DATE"

# Repo is empty OR there are no commits that mention "Change-Id"
while read -r repo; do
    COMMITS=$(curl -n -sL https://api.github.com/repos/"${repo}"/commits)
    if printf '%b\n' "$COMMITS" | jq -r '.message' 2>/dev/null | grep -q 'Git Repository is empty.'; then
        echo "$repo" >> "active-github-repos-$DATE"
        continue
    fi
    if printf '%b\n' "$COMMITS" | jq -r '.[].commit.message' 2>/dev/null | grep -q 'Change-Id'; then
        continue
    fi
    echo "$repo" >> "active-github-repos-$DATE"
done < github-repos-not-on-gerrit-"$DATE"

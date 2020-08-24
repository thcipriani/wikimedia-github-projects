#!/usr/bin/env bash
set -eu
DATE=$(date -I)

cat /dev/null > "active-github-repos-$DATE"

is_empty() {
    local commits
    commits="$1"
    printf '%s\n' "$commits" | jq -r '.message' 2>/dev/null | grep -q 'Git Repository is empty.'
}

has_change_id() {
    local commits
    commits="$1"
    printf '%s\n' "$commits" | jq -r '.[].commit.message' | grep -q 'Change-Id'
}

# Repo is empty OR there are no commits that mention "Change-Id"
while read -r repo; do
    printf 'Checking %s...\n' "$repo"
    COMMITS="$(curl -n -sL https://api.github.com/repos/"${repo}"/commits)"

    if is_empty "$COMMITS" || ! has_change_id "$COMMITS"; then
        echo "$repo" >> "active-github-repos-$DATE"
    fi

done < "github-repos-not-on-gerrit-${DATE}"

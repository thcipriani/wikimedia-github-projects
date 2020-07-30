#!/usr/bin/env bash
curl -sL https://gerrit.wikimedia.org/r/projects/?all \
	| tail -c +6 \
	| jq -r '.|to_entries|.[].key' > "gerrit-repos-$(date -I)"

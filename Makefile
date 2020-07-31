.PHONY: clean
DATE=$(shell date -I --utc)

README: active-github-repos-$(DATE)
	python3 05-add-github-repos-mirrored-to-gerrit.py

gerrit-repos-$(DATE):
	bash 01-get-gerrit-projects.sh

github-repos-$(DATE):
	python3 02-get-github-projects.py

github-repos-not-on-gerrit-$(DATE): gerrit-repos-$(DATE) github-repos-$(DATE)
	python3 03-find-github-repos-not-on-gerrit.py

active-github-repos-$(DATE): github-repos-not-on-gerrit-$(DATE)
	bash 04-github-repos-with-pull-requests.sh

clean:
	rm README

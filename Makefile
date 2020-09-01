.PHONY: clean
DATE=$(shell date -I --utc)

README: acive-github-repos-with-mirrored-$(DATE)
	python3 06-remove-mirrored-diffusion-to-github.py

gerrit-repos-$(DATE):
	bash 01-get-gerrit-projects.sh

github-repos-$(DATE):
	python3 02-get-github-projects.py

github-repos-not-on-gerrit-$(DATE): gerrit-repos-$(DATE) github-repos-$(DATE)
	python3 03-find-github-repos-not-on-gerrit.py

# active-github-repos-$(DATE): github-repos-not-on-gerrit-$(DATE)
# 	bash 04-commit-message-has-changeid.sh

active-github-repos-$(DATE): github-repos-not-on-gerrit-$(DATE)
	sort github-repos-not-on-gerrit-$(DATE) > active-github-repos-$(DATE)

acive-github-repos-with-mirrored-$(DATE): active-github-repos-$(DATE)
	python3 05-add-github-repos-mirrored-to-gerrit.py

clean:
	rm README *-$(DATE)

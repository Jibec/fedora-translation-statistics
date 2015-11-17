# Fedora-zanata-statistics
Fedora is translated via https://fedora.zanata.org/

Zanata is a free software : https://github.com/zanata/

It exposes a REST API : https://zanata.ci.cloudbees.com/job/zanata-api-site/site/zanata-common-api/rest-api-docs/index.htlm

## How to use
Copy the files

create a "results" folder

type : python3 ./getstats.py

It may be pretty slow because every one in the time, a request is very long and it waits a time out.

## How does it works
I created a list of project and interation/version in projects.csv

I make one request for every project and iteration

As a remember, this is the organization of Zanata : Group > Project > Iteration/version > Document

## Todo
Understand why I can't get the list of project via https://fedora.zanata.org/rest/projects/

Understand why I can't get the list of iteration of a project

### Possible upgrades
It is possible to get Document stats, but I don't see the need at the moment

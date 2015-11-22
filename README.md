# Fedora-zanata-statistics
Fedora is translated via https://fedora.zanata.org/

Zanata is a free software : https://github.com/zanata/

It exposes a REST API : https://zanata.ci.cloudbees.com/job/zanata-api-site/site/zanata-common-api/rest-api-docs/index.htlm

## How to use
Copy the files

create a "results" folder

type : python3 ./getstats.py

If you already ran the script, the xml file are saved in "results" folder. Make sure you delete "*stat*" file to make an update.

## How does it works
It downloads firt the list of all fedora Projets with Zanata's API.

For each _active_ project, it donwloads iteration/version list.

For earch _active_ iteration/version, it downloads statistics.

Then, a csv file is created with all results.

As a remember, this is the organization of Zanata : Group > Project > Iteration/version > Document

### Possible upgrades
It may be possible to get Document stats, but I don't see the need at the moment.

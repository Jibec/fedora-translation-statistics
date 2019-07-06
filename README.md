# Fedora-translation-statistics
Fedora is translated via https://fedora.zanata.org/

Zanata is a free software : https://github.com/zanata/

It exposes a REST API : https://zanata.ci.cloudbees.com/job/zanata-api-site/site/zanata-common-api/rest-api-docs/index.htlm

## Statistics production

### How to use

```
git clone https://github.com/Jibec/fedora-translation-statistics
cd fedora-translation-statistics
./run.sh
```

### How does it works
It downloads firt the list of all fedora Projets with Zanata's API.

For each _active_ project, it donwloads iteration/version list.

For earch _active_ iteration/version, it downloads statistics.

Then, a csv file is created with all results.

As a remember, this is the organization of Zanata : Group > Project > Iteration/version > Document

## AppData statistics

A script to get Fedora's translation status of RPM available in Fedora.

You need to download "Fedora-xx.xml" from https://alt.fedoraproject.org/pub/alt/screenshots/fxx/ (where xx is the Fedora version)

This source file is produced by Richard Hughes with : https://github.com/hughsie/appstream-glib

## TM extraction

### How to use

```
git clone https://github.com/Jibec/fedora-translation-statistics
cd fedora-translation-statistics
./get_zanata_tm.py
```

This will produce one translation memory file per project-iteration couple, whatever the project or iteration is active or not.

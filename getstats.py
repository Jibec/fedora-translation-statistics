#!/usr/bin/env python3


# -*- encoding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
#
# @author Jean-Baptiste Holcroft <jb.holcroft@gmail.com>

import csv
import requests
from xml.dom.minidom import parse, parseString, getDOMImplementation
import os.path
from os import walk
import sys

projects = []
f = []
local_path = "results/"
result_file = 'output_file.csv'

def read_projects_file():
    global projects
    # import des chaînes de traductions de nominatims pour les tags majeurs

    with open('./projects.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # structure  key, value, string
        for row in spamreader:
            projects.append((row[0], row[1], row[2]))

    return 1

print("1.Lire la liste des projets")
read_projects_file()
print("2.Récupérer chaque fichier")
for project in projects[1:]:
    projectSlug   = project[0]
    iterationSlug = project[1]
    groupSlug     = project[2]

    filePath = "%s%s___%s___%s" % (local_path, groupSlug, projectSlug, iterationSlug)
    print("%s : " % (filePath), end="")
    if os.path.isfile(filePath) != True:
        try:
            request_osm = requests.get("https://fedora.zanata.org/rest/stats/proj/%s/iter/%s?word=true" % (projectSlug, iterationSlug))
            output_file = open(filePath, 'w')
            output_file.write(request_osm.text)
            output_file.close
            print("ok", end="")
        except:
            e = sys.exc_info()
            print("Erreur %s avec %s" % (e[0], e[1]) )
    else:
        print("existe", end="")

print("3.Écrire le fichier CSV")
with open(result_file, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    first = 0
    for (dirpath, dirnames, filenames) in walk(local_path):
        for filename in filenames:
            dom = parse(local_path+filename)

            for stat in dom.getElementsByTagName("stat"):
                groupSlug, projectSlug, iterationSlug = filename.split("___")
                if first == 0:
                    ici = [i for i in stat.attributes.keys()]
                    ici.append("group")
                    ici.append("project")
                    ici.append("version/iteration")
                    spamwriter.writerow(ici)
                    first = 1
                ici = [stat.attributes[i].value for i in stat.attributes.keys()]
                ici.append(groupSlug)
                ici.append(projectSlug)
                ici.append(iterationSlug)
                spamwriter.writerow(ici)


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
# @author Jean-Baptiste Holcroft <jean-baptiste@holcroft.fr>

"""
This scripts extract translation statistics from Zanata using the API
Usage: ./read_zanata_stats.py
"""

from datetime import date
from functools import wraps
from xml.dom.minidom import parse

import csv
import errno
import os
import signal
import time
import sys
import requests

RESULT_PATH = "./results/"
RESULT_FILE = './history/zanata/output_file-%s-%s-%s.csv' % (
    date.today().year, date.today().month, date.today().day)
PROJECTS_FILE = "./results/projets.xml"


class TimeoutError(Exception):
    """ source : http://stackoverflow.com/questions/2281850 """


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """ source : http://stackoverflow.com/questions/2281850 """
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def get_projects_list():
    """ Get the full list of projects from fedora.zanata
        Save the result in a file
    """
    api_url_projects = "https://fedora.zanata.org/rest/projects"
    file_path = PROJECTS_FILE
    print("Donwload of the projects file")

    if os.path.isfile(file_path) is False:
        try:
            request_output = requests.get(api_url_projects)
            if request_output.status_code == 200:
                output_file = open(file_path, 'w')
                output_file.write(request_output.text)
                output_file.close()
        except requests.exceptions.HTTPError:
            error = sys.exc_info()
            print("Error %s : %s" % (error[0], error[1]))
    else:
        print("The file '%s' already exist !" % file_path)


def download_project_iteration(project_id):
    """ download the project description and return iteration list
    """
    iterations = []

    file_path = "%sproject_iterations_%s.xml" % (RESULT_PATH, project_id)
    api_url_project = "https://fedora.zanata.org/rest/projects/p/%s" % project_id
    try:
        if get_via_resquet_and_write(api_url_project, file_path) == 1:
            return iterations
    except TimeoutError:
        error = sys.exc_info()
        print("Timeout error %s : %s with project/iteration %s" %
              (error[0], error[1], file_path))
        return iterations

    dom = parse(file_path)
    for stat in dom.getElementsByTagName("ns2:project-iteration"):
        iteration_id = stat.getAttributeNode('id').nodeValue
        iteration_status = stat.getElementsByTagName("status")[
            0].firstChild.data
        if iteration_status == "ACTIVE":
            iterations.append(iteration_id)

    return iterations


def get_projects_iterations():
    """ For each project in projects file file
        Get projects iterations/versions from fedora.zanata
        Then append the list to the global result list """
    projects = []

    dom = parse(PROJECTS_FILE)
    current_line = 0
    total_line = len(dom.getElementsByTagName("ns2:project"))

    for stat in dom.getElementsByTagName("ns2:project"):
        current_line += 1
        project_id = stat.getAttributeNode('id').nodeValue
        project_status = stat.getElementsByTagName("status")[0].firstChild.data
        print("   %s/%s - %s" % (current_line, total_line, project_id))
        if project_status == "ACTIVE":
            for iteration in download_project_iteration(project_id):
                projects.append((project_id, iteration))

    return projects


def get_projects_statistics(projects):
    """ for each existing projets, download statistic file
    """
    current_line = 0
    total_line = len(projects[1:])

    for project in projects[1:]:
        project_slug = project[0]
        iteration_slug = project[1]

        file_path = "%sproject_stat___%s___%s" % (
            RESULT_PATH, project_slug, iteration_slug)
        current_line += 1
        print("   %s/%s - %s %s" %
              (current_line, total_line, project_slug, iteration_slug))

        request = "https://fedora.zanata.org/rest/stats/proj/%s/iter/%s?word=true" % (
            project_slug, iteration_slug)
        try:
            get_via_resquet_and_write(request, file_path)
        except TimeoutError:
            err = sys.exc_info()
            print("Timeout error %s : %s with project/iteration %s" %
                  (err[0], err[1], file_path))


@timeout(30)
def get_via_resquet_and_write(request, file_name):
    """ get a requet and save it to file if it worked
    """
    if os.path.isfile(file_name) is False:
        try:
            request_output = requests.get(request)
            if request_output.status_code == 200:
                output_file = open(file_name, 'w')
                output_file.write(request_output.text)
                output_file.close()
                while output_file.closed is False:
                    time.sleep(0.1)
            return request_output.status_code
        except requests.exceptions.ConnectionError:
            error = sys.exc_info()
            print("Connection error %s : %s with project/iteration %s" %
                  (error[0], error[1], file_name))
            return 1
    return 0


def get_global_statistics():
    """ for each downloaded xml file, read it and add stats to global csv file
    """
    with open(RESULT_FILE, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        first = 0
        for (_, _, filenames) in os.walk(RESULT_PATH):
            for filename in filenames:
                if filename[0:12] == "project_stat":
                    dom = parse(RESULT_PATH+filename)
                    trash, project_slug, iteration_slug = filename.split("___")
                    # print("%s %s %s %s" % (trash, project_slug, iteration_slug, filename))
                    for stat in dom.getElementsByTagName("stat"):
                        ici = []
                        if first == 0:
                            ici = [i for i in stat.attributes.keys()]
                            ici.append("project")
                            ici.append("version/iteration")
                            spamwriter.writerow(ici)
                            first = 1
                        ici = [
                            stat.attributes[i].value for i in stat.attributes.keys()]
                        ici.append(project_slug)
                        ici.append(iteration_slug)
                        spamwriter.writerow(ici)


def main():
    """ call each functions
    """
    projects = []

    print("0. Get projects list")
    get_projects_list()

    print("1. Get projects iterations")
    projects = get_projects_iterations()

    print("2. Get each statistics")
    get_projects_statistics(projects)

    print("3. Write statistics in csvfile")
    get_global_statistics()

    print("4. Done !")


if __name__ == '__main__':
    main()

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
# TODO : add keywords statistics

import xml.etree.ElementTree as ET
import csv
from datetime import date

import statistics

STATISTIC_FILE = 'fedora-23.xml'
RESULT_FILE = './AppData-Global-detailed-%s-%s-%s.csv' \
    % (date.today().year, date.today().month, date.today().day)

NS_KEY = "http://www.w3.org/XML/1998/namespace"
NS_MAP = {"xml": NS_KEY}

TRANSLATABLE_FIELDS = ["name", "summary", "description"]
languages = []
projects_statistics = {}

# open global xml file
tree = ET.parse(STATISTIC_FILE)
root = tree.getroot()

#
# GLOBAL STATISTICS
#
print("Make global statistics")
# initiate list of languages
for i in root.findall(".//*[@xml:lang]", namespaces=NS_MAP):
    lang = i.get("{%s}lang" % NS_KEY)
    languages.append(lang)
languages = list(set(languages))
languages = languages.copy()

output_for_csv = []
header_line = ["project", "type", "url"] + languages
output_for_csv.append(header_line)

for component in root.findall("component"):
    package_name = component.find("pkgname").text
    package_type = component.get("type")
    package_homepage = ""
    language_statistic = [0] * len(languages)

    # get project url
    for url in component.findall("url"):
        if url.get("type") == "homepage":
            package_homepage = url.text

    # get project statistics
    for translatable_field in TRANSLATABLE_FIELDS:
        for field in component.findall(translatable_field):
            lang = field.get("{%s}lang" % NS_KEY)
            if lang != None:
                language_statistic[languages.index(lang)] += 1 / len(TRANSLATABLE_FIELDS)

    package_info = [package_name, package_type, package_homepage]
    csv_line = package_info + language_statistic

    output_for_csv.append(csv_line)

with open(RESULT_FILE, 'w', newline='') as csvfile:
    result_file_csv = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in output_for_csv:
        result_file_csv.writerow(row)

def one_language_stats(lang):
    #
    # search for one language
    #
    output_for_csv_langage_detailed = []
    header_line = ["project", "type", "url"] + TRANSLATABLE_FIELDS + ["package stats"]
    output_for_csv_langage_detailed.append(header_line)

    for component in root.findall("component"):
        package_name = component.find("pkgname").text
        package_type = component.get("type")
        package_homepage = ""
        language_statistic = [0] * len(TRANSLATABLE_FIELDS)
        embedded_statistic = [0]

        # get project url
        for url in component.findall("url"):
            if url.get("type") == "homepage":
                package_homepage = url.text

        for translatable_field in TRANSLATABLE_FIELDS:
            for field in component.findall(translatable_field):
                lang_field = field.get("{%s}lang" % NS_KEY)
                if lang_field == lang:
                    language_statistic[TRANSLATABLE_FIELDS.index(translatable_field)] = "yes"

        for field in component.findall(".//lang"):
            if field.text == lang:
                percent = field.get("percentage")
                if percent == None:
                    percent = 1
                embedded_statistic[0] = int(percent)/100

        package_info = [package_name, package_type, package_homepage]
        csv_line = package_info + language_statistic + embedded_statistic
        output_for_csv_langage_detailed.append(csv_line)

    result_file_langage = './AppData_Detailed_%s-%s-%s-%s.csv' \
        % (lang, date.today().year, date.today().month, date.today().day)

    with open(result_file_langage, 'w', newline='') as csvfile:
        result_file_csv = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in output_for_csv_langage_detailed:
            result_file_csv.writerow(row)

    return output_for_csv_langage_detailed

def to_number(val):
    """
    Transform values to percentage
    """
    if val == "yes":
        return 1
    else:
        return int(val)

def give_stat(header, field, results_list, filter_field = None, filter_value = None):
    """
    Return list
    """
    if filter_field != None and filter_value != None:
        results = [to_number(stat[header.index(field)]) \
                      for stat in results_list \
                      if stat[header.index(filter_field)] == filter_value]
    else:
        results = [to_number(stat[header.index(field)]) \
                      for stat in results_list]

    mean = round(statistics.mean(results)*100,2)
    pstdev = round(statistics.pstdev(results)*100,2)

    return [field,filter_field,filter_value, mean, pstdev, len(results)]

def make_lang_stats(stats):
    """
    Calculation of statistics
    """
    results = []
    # Global stats

    for field in ["name", "summary", "description", "package stats"]:
        results.append(give_stat(stats[0], field, stats[1:]))

    # Desktop stats

    for field in ["name", "summary", "description", "package stats"]:
        results.append(give_stat(stats[0], field, stats[1:], "type","desktop"))

    return results

langage_statistics = []
header = ["lang","field","filter","filter_value", "mean", "pstdev", "number of packages"]
langage_statistics.append(header)

for lang in languages:
    print("Make statistics for language %s (%s/%s)" % (lang, languages.index(lang), len(languages)))
    lang_results = one_language_stats(lang)
    results = make_lang_stats(lang_results)

    for result in results:
        langage_statistics.append([lang]+result)

result_file_langage = './AppData_Global_Statistics_%s-%s-%s.csv' \
    % (date.today().year, date.today().month, date.today().day)
with open(result_file_langage, 'w', newline='') as csvfile:
    result_file_csv = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in langage_statistics:
        result_file_csv.writerow(row)

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
# TODO : add keywords statistics

"""
This scripts extract translation statistics from app data files consolidated in
https://alt.fedoraproject.org/pub/alt/screenshots/fxx/ (where xx is the Fedora version)
Usage: ./read_appdata_stats.py
"""

from datetime import date

import argparse
import csv
import xml.etree.ElementTree as ET
import gzip
import os
import requests
import shutil
import statistics

NS_KEY = "http://www.w3.org/XML/1998/namespace"
NS_MAP = {"xml": NS_KEY}

TRANSLATABLE_FIELDS = ["name", "summary", "description"]


def one_language_stats(lang, root):
    """
    search for one language
    """
    output = []
    header_line = ["project", "type", "url"] + \
        TRANSLATABLE_FIELDS + ["package stats"]
    output.append(header_line)

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
                    language_statistic[TRANSLATABLE_FIELDS.index(
                        translatable_field)] = "yes"

        for field in component.findall(".//lang"):
            if field.text == lang:
                percent = field.get("percentage")
                if percent is None:
                    percent = 1
                embedded_statistic[0] = int(percent)/100

        output.append(
            [package_name, package_type, package_homepage] + language_statistic + embedded_statistic)

    write_in_file("AppData_Detailed_"+lang+"-%s-%s-%s.csv", output)

    return output


def to_number(val):
    """
    Transform values to percentage
    """
    if val == "yes":
        return 1

    return int(val)


def give_stat(header, field, results_list, filter_field=None, filter_value=None):
    """
    Return list
    """
    if filter_field is not None and filter_value is not None:
        results = [to_number(stat[header.index(field)])
                   for stat in results_list
                   if stat[header.index(filter_field)] == filter_value]
    else:
        results = [to_number(stat[header.index(field)])
                   for stat in results_list]

    mean = round(statistics.mean(results)*100, 2)
    pstdev = round(statistics.pstdev(results)*100, 2)

    return [field, filter_field, filter_value, mean, pstdev, len(results)]


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
        results.append(
            give_stat(stats[0], field, stats[1:], "type", "desktop"))

    return results


def get_language_list(root):
    """ return every existing languages in xml file
    """
    languages = []

    # initiate list of languages
    for i in root.findall(".//*[@xml:lang]", namespaces=NS_MAP):
        lang = i.get("{%s}lang" % NS_KEY)
        languages.append(lang)
    languages = list(set(languages))
    languages = languages.copy()
    languages.sort(key=str.lower)

    return languages


def compute_global_stats(root, languages):
    """ produce a csv file with all languages
    """
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
                if lang is not None:
                    language_statistic[languages.index(
                        lang)] += 1 / len(TRANSLATABLE_FIELDS)

        package_info = [package_name, package_type, package_homepage]
        csv_line = package_info + language_statistic

        output_for_csv.append(csv_line)

    write_in_file("AppData-Global-detailed-%s-%s-%s.csv", output_for_csv)


def compute_per_language_stats(root, languages):
    """ compute per language stats and consolidate results
    """
    langage_statistics = []
    header = ["lang", "field", "filter", "filter_value",
              "mean", "pstdev", "number of packages"]
    langage_statistics.append(header)

    for lang in languages:
        print("  Make statistics for language %s (%s/%s)" %
              (lang, languages.index(lang)+1, len(languages)))
        lang_results = one_language_stats(lang, root)
        results = make_lang_stats(lang_results)

        for result in results:
            langage_statistics.append([lang]+result)

    write_in_file("AppData_Global_Statistics_%s-%s-%s.csv", langage_statistics)


def write_in_file(file_mask, content):
    """ store results in csv file
    """
    file_name = "./history/appdata/f30_" + \
        file_mask % (date.today().year, date.today().month, date.today().day)

    with open(file_name, 'w', newline='') as csvfile:
        result_file_csv = csv.writer(
            csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in content:
            result_file_csv.writerow(row)


def download_file(url, filename):
    """ download file
    """
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


def get_xml_file(version):
    """ open xml file, download it if missing
    """
    appdata_file = "fedora-{v}.xml".format(v=version)

    if os.path.isfile(appdata_file) is not True:
        url = "https://dl.fedoraproject.org/pub/alt/screenshots/f{v}/fedora-{v}.xml.gz".format(
            v=version)
        gzip_file = "fedora-{v}.xml.xz".format(v=version)

        download_file(url, gzip_file)

        with gzip.open(gzip_file, 'rb') as f_in:
            with open(appdata_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(gzip_file)

    tree = ET.parse(appdata_file)

    return tree.getroot()


def main():
    """ call each functions
    """

    parser = argparse.ArgumentParser(
        description="Computes language stats for each appdata file")
    parser.add_argument("--version", required=True, type=int,
                        choices=range(20, 31),
                        help="Only work on one SRPM, if selected")

    args = parser.parse_args()

    print("0. Open xml file")
    root = get_xml_file(args.version)

    print("1. Deduct the list of languages")
    languages = get_language_list(root)

    print("2. compute_global_stats")
    compute_global_stats(root, languages)

    print("3. compute_per_language_stats")
    compute_per_language_stats(root, languages)

    print("4. Done !")


if __name__ == '__main__':
    main()

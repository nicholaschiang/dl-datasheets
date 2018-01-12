#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import itertools
import re
import urllib
import urllib2
import urlparse
import posixpath
from hardware_normalizers import *

def get_url_filename(url):
    # Right now, we will always filter duplicate PDFs.
    if url == '-' or url is None:
        return "N/A"

    # Append 'http:' if none is found in the url. This is because
    # Digikey sometimes has "//media.digikey.com/..." urls.
    if not url.startswith("http"):
        url = "http:" + url
    # print(url)
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(url)

        path = urlparse.urlsplit(url).path
        basename = posixpath.basename(path)

        # NOTE: This is to handle the weird filehandler URLs
        # such as http://www.microchip.com/mymicrochip/filehandler.aspx?ddocname=en011815
        # or https://toshiba.semicon-storage.com/info/docget.jsp?did=11316&prodName=TC75S101F
        # Reference: http://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way
        if not (basename.endswith('.pdf') or basename.endswith(".PDF")):
            if response.info().has_key('Content-Disposition'):
                basename = response.info()['Content-Disposition'].split('filename=')[1]
                if basename[0] == '"' or basename[0] == "'":
                    basename = basename[1:-1]
            elif url != response.url: # if we were redirected, get filename from new URL
                unique_urls.add(response.url) # track unique urls
                path = urlparse.urlsplit(response.url).path
                basename = posixpath.basename(path)

        basename = re.sub('[^A-Za-z0-9\.\-\_]+', '', basename) # strip away weird characters
        outfile = basename # just type the original filename

        if not (outfile.endswith('.pdf') or outfile.endswith(".PDF")):
            outfile = outfile + ".pdf"

        # Lowercase everything to ensure consistency in extensions and remove more duplicates
        # print(outfile.lower()[:-4])
        return outfile.lower()[:-4] # without the extension
    except Exception as e:
        # print(e)
        return "N/A"

def preprocess_gbp(typ_gpb):
    if typ_gpb == '-':
        return "N/A"
    else:
        return typ_gpb[:-3] + " " + typ_gpb[-3:] # add space between num and unit

def preprocess_supply_current(current):
    supply_current = current.replace("Â", '').replace('µ', 'u')

    # sometimes digikey reports a random MAX.
    supply_current = supply_current.replace("(Max)", '').strip()

    if supply_current == '-':
        return "N/A"
    else: # add space between number and unit
        return supply_current[:-2] + " " + supply_current[-2:]

def preprocess_operating_voltage(voltage):
    # handle strings like:
    #   2.4 V ~ 6 V
    #   4.5 V ~ 36 V, Â±2.25 V ~ 18 V
    #   10 V ~ 36 V, Â±5 V ~ 18 V
    #   4.75 V ~ 5.25 V, Â±2.38 V ~ 2.63 V
    if voltage == '-':
        return ("N/A", "N/A")

    op_volt = voltage.replace("Â", '')
    if '~' not in op_volt and ',' in op_volt:
        op_volt = op_volt.replace(',', '~')
    elif '~' not in op_volt: # handle cases where only a single value is reported
        op_volt = " ~ ".join([op_volt, op_volt])
    ranges = [r.strip() for r in op_volt.split(',')]
    min_set = set()
    max_set = set()
    for r in ranges:
        try:
            (min_val, max_val) = ([val.strip() for val in r.split('~')])
            if ('/' in min_val or '/' in max_val):
                continue # -0.9 V/+1.3 V-0.9 V/+1.3 V in ffe002af_13.csv
            if (' ' not in min_val):
                min_val = min_val[:-1] + " " + min_val[-1:]
            if (' ' not in max_val):
                max_val = max_val[:-1] + " " + max_val[-1:]
            min_set.add(min_val)
            max_set.add(max_val)
        except ValueError:
            print("[ERROR] preprocessing operating voltage: \"%s\" returning N/A." % voltage)
            return ("N/A", "N/A")

    return (';'.join(min_set), ';'.join(max_set))

def preprocess_operating_temp(temperature):
    if temperature == '-':
        return ("N/A", "N/A")
    # handle strings like:
    #   -20Â°C ~ 75Â°C
    op_temp = temperature.replace("Â", '').replace('°', ' ')

    return ([val.strip() for val in op_temp.split('~')])


def format_digikey_gold(raw_gold_file, formatted_gold_file, seen, append=False):
    delim = ';'
    with open(raw_gold_file, "r") as csvinput, open(formatted_gold_file, "a") if append else open(formatted_gold_file, "w") as csvoutput:
        writer = csv.writer(csvoutput, lineterminator="\n")
        reader = csv.reader(csvinput)
        next(reader, None)  # Skip header row
        for line in reader:
            # TODO: Do we want to just skip adding the ones that have missing docs?
            doc_name = get_url_filename(line[0])
            part_num = line[3]
            manufacturer = line[4] # TODO: These don't match
            typ_gbp = preprocess_gbp(line[18])
            typ_supply_current = preprocess_supply_current(line[22])
            (min_op_supply_volt, max_op_supply_volt) = preprocess_operating_voltage(line[24])
            (min_op_temp, max_op_temp) = preprocess_operating_temp(line[25])

            # Map each attribute to its corresponding normalizer
            name_attr_norm = [
                ('typ_gbp', typ_gbp, gain_bandwidth_normalizer),
                ('typ_supply_current', typ_supply_current, supply_current_normalizer),
                ('min_op_supply_volt', min_op_supply_volt, opamp_voltage_normalizer),
                ('max_op_supply_volt', max_op_supply_volt, opamp_voltage_normalizer),
                ('min_op_temp', min_op_temp, temperature_normalizer),
                ('max_op_temp', max_op_temp, temperature_normalizer)]

            part_num = opamp_part_normalizer(part_num)

            # Output tuples of each normalized attribute
            for name, attr, normalizer in name_attr_norm:
                if 'N/A' not in attr:
                    for a in attr.split(delim):
                        if len(a.strip()) > 0:
                            output = [doc_name, part_num, name, normalizer(a)]
                            if tuple(output) not in seen:
                                writer.writerow(output)
                                seen.add(tuple(output))


if __name__ == '__main__':
    digikey_csv_dir = "/home/lwhsiao/repos/sensys/code/digikey_scraper/opamp_csv/"
    formatted_gold = '/home/lwhsiao/repos/sensys/code/gold_utils/opamp_digikey_gold.csv'
    seen = set()
    for i, filename in enumerate(sorted(os.listdir(digikey_csv_dir))):
        if filename.endswith(".csv"):
            raw_path = os.path.join(digikey_csv_dir, filename)
            print("[info] Parsing %s" % raw_path)
            if i == 0: # create file on first iteration
                format_digikey_gold(raw_path, formatted_gold, seen)
            else: # then just append to that same file
                format_digikey_gold(raw_path, formatted_gold, seen, append=True)

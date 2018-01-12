#! /usr/bin/env python

import sys, os
import re
import urllib
import urllib2
import time
import argparse
import csv
from pprint import pprint

def parse_args():
    """
    Parse the arguments for the directory to read from and save to.
    """
    # Define what commandline arguments can be accepted
    parser = argparse.ArgumentParser()
    parser.add_argument('src_dir',metavar="CSV_DIRECTORY",
                        help="Source directory containing Digikey CSV files.")
    parser.add_argument('dest_dir',metavar="SAVE_DIRECTORY",
                        help="Directory to save the PDF datasheets to.")
    parser.add_argument('--verbose', dest='verbose', action='store_true', help="show http response errors.")
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.0')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    return args.src_dir, args.dest_dir, args.verbose

def normalize_part(old_part):
    old_part = old_part.rsplit(",")[0] # Drop the stuff after a comma
    old_part = old_part.replace("(Q)", '') # drop (Q) for toshiba
    old_part = old_part.replace("(F)", '') # drop (F) for toshiba
    old_part = old_part.replace(' ', '') # remove whitespace
    old_part = old_part.replace('/GOLD', '') # remove "/GOLD"
    old_part = old_part.upper()
    return old_part

def create_part_dictionary(src, dest, verbose):
    """
    For each CSV at the 1st level of the src directory, download the datasheet
    and save it to the destination directory.
    """
    # To make indexind into Digikey CSV more readable
    MANUF = 4
    PARTNUM = 3
    DATASHEET = 0

    total_count = 0

    # Check that src and dest have trailing slash
    if not src.endswith('/'):
         src = src + '/'
    if not dest.endswith('/'):
         dest = dest + '/'

    # Check for destination directory
    # NOTE: There is technically a race condition here that could throw an
    # exception. But, it's unlikely that the directory will suddenly be created
    # between the if-statement and the creation of it by this code.
    if not os.path.exists(dest):
        os.makedirs(dest)

    dest = dest + "digikey_part_dictionary.csv"

    all_parts = set()

    for filename in os.listdir(src):
        if filename.endswith(".csv"):
            path = os.path.join(src, filename)
            print('[info] Parsing from %s' % path)
            with open(path, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                next(reader, None) # skip header row
                for row in reader:
                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]
                    part = row[PARTNUM]
                    part = normalize_part(part)
                    url = url.strip().replace(",", "%2C")
                    if url.startswith("//"):
                        url = "http:" + url
                    all_parts.add((part, url))
                    total_count += 1


    print '[info] Parse %d parts.' % total_count

    outfile = open(dest, 'w')
    for part, url in all_parts:
        if url == '' or url == '-':
            url = "N/A"
        outfile.write(part + ', ' + url + "\n")

# Main Function
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    src, dest, verbose= parse_args()    # Parse commandline arguments
    start_time = time.time()
    print '[info] Downloading datasheets found in %s' % src
    create_part_dictionary(src, dest, verbose)
    finish_time = time.time()
    print '[info] Took', finish_time - start_time, 'sec total.'

#! /usr/bin/env python

import sys, os
import re
import urllib
import urllib2
import time
import argparse
import csv
from pprint import pprint

# Algorithm:
# 1. Iterate over documents in test. Find a row that matches the filename MANUF_PART. Save URL of this test doc.
# 2. Create set of all URLs of test documents. Hopefully this is 75.
# 3. Iterate over all CSV files again and output rows matching this URL to new CSV file.




def parse_args():
    """
    Parse the arguments for the directory to read from and save to.
    """
    # Define what commandline arguments can be accepted
    parser = argparse.ArgumentParser()
    parser.add_argument('src_dir',metavar="CSV_DIRECTORY",
                        help="Source directory containing Digikey CSV files.")
    parser.add_argument('test_dir',metavar="TEST_DIRECTORY",
                        help="Source directory containing test files.")
    parser.add_argument('dest_csv',metavar="SAVE_DIRECTORY",
                        help="Filename to save the test CSV to.")
    parser.add_argument('--verbose', dest='verbose', action='store_true', help="show http response errors.")
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.0')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    return args.src_dir, args.test_dir, args.dest_csv, args.verbose

def create_test_csv(csv_src, pdf_src, dest, verbose):
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
    if not csv_src.endswith('/'):
         csv_src = csv_src + '/'
    if not pdf_src.endswith('/'):
         pdf_src = pdf_src + '/'
    if not dest.endswith('.csv'):
         dest = dest + '.csv'

    # Iterate over test PDFs, create set of filenames
    if verbose:
        print("[info] Collecting Test PDF Filenames...")
    pdf_filenames = set()
    for filename in os.listdir(pdf_src):
        if filename.endswith(".pdf"):
            pdf_filenames.add(filename)

    if verbose:
        print("[info] # of test PDFs: " + str(len(pdf_filenames)))

    # Iterate over CSVs to create set of URLs corresponding to the test PDFs
    if verbose:
        print("[info] Collecting Test PDF URLS...")

    pdf_urls = set()
    for filename in os.listdir(csv_src):
        if filename.endswith(".csv"):
            path = os.path.join(csv_src, filename)
            with open(path, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                next(reader, None) # skip header row
                for row in reader:
                    potential_filename = re.sub('[^A-Za-z0-9]+', '', row[MANUF]) + '_' + re.sub('[^A-Za-z0-9]+', '', row[PARTNUM]) + ".pdf"
                    if potential_filename in pdf_filenames:
                        pdf_urls.add(row[DATASHEET])

                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]


    if verbose:
        print("[info] # of test PDF URLs found: " + str(len(pdf_urls)))

    if verbose:
        print("[info] Copying rows from digikey CSVs to new file for test PDFs...")

    # 2nd pass through digikey CSVs to copy out relevant rows.
    with open(dest, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for filename in os.listdir(csv_src):
            if filename.endswith(".csv"):
                path = os.path.join(csv_src, filename)
                with open(path, 'rb') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    next(reader, None) # skip header row
                    for row in reader:
                        if row[DATASHEET] in pdf_urls:
                            writer.writerow(row)

# Main Function
# /home/lwhsiao/Desktop/transistors/single-bjt
# /home/lwhsiao/repos/snorkel/tutorials/tables/data/hardware/test/pdf
# test_data.csv
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    csvs, pdfs, dest, verbose = parse_args()    # Parse commandline arguments
    start_time = time.time()
    create_test_csv(csvs, pdfs, dest, verbose)
    finish_time = time.time()
    print '[info] Took', finish_time - start_time, 'sec total.'

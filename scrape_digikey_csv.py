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

def download_datasheets(src, dest, verbose):
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

    for filename in os.listdir(src):
        page_count = -1
        if filename.endswith(".csv"):
            path = os.path.join(src, filename)
            print('[info] Downloading from %s' % path)
            with open(path, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:

                    # skip the header row
                    if page_count == -1:
                        page_count += 1
                        continue

                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]

                    # Append 'http:' if non is found in the url. This is because
                    # Digikey sometimes has "//media.digikey.com/..." urls.
                    if not url.startswith("http"):
                        url = "http:" + url

                    if url is not None and url != '-':
                        # Download the PDF
                        try:
                            outfile =  dest + re.sub('[^A-Za-z0-9]+', '', row[MANUF]) + '_' + re.sub('[^A-Za-z0-9]+', '', row[PARTNUM]) + ".pdf"
                            print "[info]   Saving %s" % outfile
                            response = urllib2.urlopen(url)
                            file = open(outfile, 'w')
                            file.write(response.read())
                            file.close()
                            page_count += 1
                        except urllib2.HTTPError, err:
                            if verbose:
                                if err.code == 404:
                                    print "[error] Page not found!..."
                                elif err.code == 403:
                                    print "[error] Access Denied!"
                                else:
                                    print "[error] HTTP Error code ", err.code
                            continue # advance to next datasheet rather than crashing
                        except urllib2.URLError:
                            if verbose:
                                print "[error] URLError."
                            continue
                        except:
                            print "[error] urllib2 error."
                            continue

                        time.sleep(0.4) # Limit ourselves to ~3 HTTP Requests/second
            total_count += page_count

    print '[info] Downloaded %d datasheets.' % total_count

# Main Function
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    src, dest, verbose= parse_args()    # Parse commandline arguments
    start_time = time.time()
    print '[info] Downloading datasheets found in %s' % src
    download_datasheets(src, dest, verbose)
    finish_time = time.time()
    print '[info] Took', finish_time - start_time, 'sec total.'

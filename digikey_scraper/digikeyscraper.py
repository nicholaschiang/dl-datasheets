#! /usr/bin/env python

import argparse
import csv
import logging
import os
import posixpath
import re
import subprocess
import sys
import time
import urllib
import urllib2
import urlparse
from pprint import pprint

import requests
from tqdm import tqdm, trange

import scraper_args

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s] %(name)s - %(message)s",
    filename="digikey.log",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# To make indexing into Digikey CSV more readable
MANUF = 4
PARTNUM = 3
DATASHEET = 0

def filter_ocr(pdf_dir):
    """
    Use `pdffonts` to check for PDFs that are just images and would require OCR.
    """
    logger.info("Begin removing PDFs that need OCR...")
    count = 0
    src_files = os.listdir(pdf_dir)
    for pdf in src_files:
        if (pdf == ".DS_Store"):
            continue

        pdf_filename = os.path.join(pdf_dir, pdf)

        if (os.path.isfile(pdf_filename)):
            try:
                output = subprocess.check_output(["pdffonts", pdf_filename], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                # Error usually means we got a HTML file instead of an actual PDF.
                logger.debug("pdffonts error on %s. Removing." % pdf_filename)
                os.remove(pdf_filename)
                count += 1
                continue
            # output = subprocess.Popen(["pdffonts", pdf_filename], stdout=subprocess.PIPE).communicate()[0]
            if (len(output.split('\n')) <= 3):
                count += 1
                # this has no fonts and thus is an image.
                logger.debug("OCR Filtering: " + pdf_filename)
                os.remove(pdf_filename)

    logger.info("Finished removing %s PDFs that needed OCR." % count)

def filter_encrypted(pdf_dir):
    """
    Remove PDFs that are encrypted, since Acrobat cannot convert them to HTML.
    """
    pattern = re.compile(r"Encrypted:\s*yes", re.U)
    logger.info("Begin removing PDFs that are encrypted...")
    count = 0
    src_files = os.listdir(pdf_dir)
    for pdf in src_files:
        if (pdf == ".DS_Store"):
            continue

        pdf_filename = os.path.join(pdf_dir, pdf)

        if (os.path.isfile(pdf_filename)):
            try:
                output = subprocess.check_output(["pdfinfo", pdf_filename], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                # Error usually means we got a HTML file instead of an actual PDF.
                logger.debug("pdfinfo error on %s. Removing." % pdf_filename)
                os.remove(pdf_filename)
                count += 1
                continue
            # Matching for lines that look like this:
            # Encrypted:      yes (print:yes copy:yes change:no addNotes:no algorithm:RC4)
            if (pattern.search(output)):
                count += 1
                # this has no fonts and thus is an image.
                logger.debug("Encrypted Filtering: " + pdf_filename)
                os.remove(pdf_filename)

    logger.info("Finished removing %s PDFs that were encrypted." % count)

def expected_unique_pdfs(csv_dir):
    """
    Count the number of unique datasheet URLs found in the CSV files.
    """
    unique_urls = set()

    for filename in sorted(os.listdir(csv_dir)):
        if filename.endswith(".csv"):
            path = os.path.join(csv_dir, filename)
            logger.debug('Counting URLs from %s' % path)
            with open(path, 'rb') as csvinput:
                reader = csv.reader(csvinput)
                next(reader, None) # skip the header row
                for row in reader:
                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]

                    # Right now, we will always filter duplicate PDFs.
                    if not (url == '-' or url is None):
                        unique_urls.add(url)
    logger.info("Expected unique PDFs: %d" % len(unique_urls))

def download_csv(csv_dir, fv_code, pages):
    """
    Scrape the CSV data from the Digikey website for the specified product family.
    """
    print("Downloading CSVs...")

    data= {
        'fv' : fv_code, # 'ffe002af' for op-amps and 'ffe001b4' for circular connectors
        'mnonly':'0',
        'newproducts':'0',
        'ColumnSort':'0',
        'page':'1',
        'stock':'0',
        'pbfree':'0',
        'rohs':'0',
        'quantity':'0',
        'ptm':'0',
        'fid':'0',
        'pageSize':'500'
    }
    logger.info("Downloading " + str(pages) + " pages...")
    for i in trange(pages):
        # Make a bunch of files since each page starts with the CSV header.
        # We don't want random header rows in the CSV file.
        filename = csv_dir + fv_code + "_" + str(i) + ".csv"
        target = open(filename,'w')
        data['page'] = i+1
        r = requests.get('http://www.digikey.com/product-search/download.csv',params=data)
        target.write(r.text.encode('utf-8'))
        target.close()
        logger.debug("Saved CSV: " + filename)



def download_pdf(src, dest):
    """
    For each CSV at the 1st level of the src directory, download the datasheet
    and save it to the destination directory.
    """

    print("Downloading PDFs...")

    total_count = 0

    unique_urls = set()

    #progress bar
    for filename in tqdm(sorted(os.listdir(src))):
        if filename.endswith(".csv"):
            path = os.path.join(src, filename)
            logger.info('Downloading from %s' % path)
            with open(path, 'rb') as csvinput:
                reader = csv.reader(csvinput)
                next(reader, None) # skip the header row
                for row in reader:
                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]
                    manuf = re.sub('[^A-Za-z0-9\-\_]+', '', row[MANUF])
                    partnum = re.sub('[^A-Za-z0-9\-\_]+', '', row[PARTNUM])

                    # Right now, we will always filter duplicate PDFs.
                    if url == '-' or url is None or url in unique_urls:
                        continue

                    # Append 'http:' if none is found in the url. This is because
                    # Digikey sometimes has "//media.digikey.com/..." urls.
                    if not url.startswith("http"):
                        url = "http:" + url

                    try:
                        opener = urllib2.build_opener()
                        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')]
                        response = opener.open(url)
                        unique_urls.add(url) # track unique urls

                        # outfile =  dest + re.sub('[^A-Za-z0-9]+', '', row[MANUF]) + '_' + re.sub('[^A-Za-z0-9]+', '', row[PARTNUM]) + ".pdf"
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

                        # basename = re.sub('[^A-Za-z0-9\.\-\_]+', '', basename) # strip away weird characters
                        outfile = dest + manuf + "_" + partnum + ".pdf"  # just type the original filename

                        if not (outfile.endswith('.pdf') or outfile.endswith(".PDF")):
                            outfile = outfile + ".pdf"

                        # Lowercase everything to ensure consistency in extensions and remove more duplicates
                        outfile = outfile.lower()

                        logger.debug("   Saving %s" % outfile)
                        pdf_file = open(outfile, 'w')
                        pdf_file.write(response.read())
                        pdf_file.close()
                        total_count += 1
                    except urllib2.HTTPError, err:
                        if err.code == 404:
                            logger.error("    Page not found: %s" % url)
                        elif err.code == 403:
                             # These can mostly be avoided by specifying a user-agent
                             # http://stackoverflow.com/questions/11450649/python-urllib2-cant-get-google-url
                            logger.error("    Access Denied: %s" % url)
                        else:
                            logger.error("    HTTP Error code %s for %s" % (err.code, url))
                        continue # advance to next datasheet rather than crashing
                    except urllib2.URLError:
                        logger.error("    urllib2.URLError for %s" % url)
                        continue
                    except Exception as e:
                        logger.error("Exception %s on URL %s" % (e, url))
                        continue

                    time.sleep(0.1) # Limit our HTTP Requests rate slightly for courtesy.
    logger.info('Downloaded %d datasheets.' % total_count)

# Main Function
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    scraper_args.parse_args()    # Parse commandline arguments
    start_time = time.time()
    logger.info('Creating PDF dataset from datasheets in %s' % scraper_args.get_fv_code())

    # First, download all the table entries from Digikey in a single CSV
    if not scraper_args.skip_csv_dl():
        download_csv(scraper_args.get_csv_dir(), scraper_args.get_fv_code(), scraper_args.get_csv_pages())

    # Print the expected number of unique PDFs
    expected_unique_pdfs(scraper_args.get_csv_dir())

    # Next, use the saved CSV to download the datasheets
    if not scraper_args.skip_pdf_dl():
        download_pdf(scraper_args.get_csv_dir(), scraper_args.get_pdf_dir())

    # Filter out the encrypted PDFs
    if not scraper_args.keep_encrypted():
        filter_encrypted(scraper_args.get_pdf_dir())

    # Filter out the PDFs that need OCR
    if not scraper_args.keep_ocr():
        filter_ocr(scraper_args.get_pdf_dir())



    finish_time = time.time()
    logger.info('Took ' + str(finish_time - start_time) + ' sec total.')

#! /usr/bin/env python

import requests
import sys, os
import re
import urllib
import urllib2
import time
import argparse
import csv
from pprint import pprint
import subprocess
import urlparse
import posixpath

import scraper_logging
import scraper_args

# To make indexing into Digikey CSV more readable
MANUF = 4
PARTNUM = 3
DATASHEET = 0

def filter_ocr(pdf_dir):
    """
    Use `pdffonts` to check for PDFs that are just images and would require OCR.
    """
    scraper_logging.debug_print("Begin removing PDFs that need OCR...")
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
                scraper_logging.debug_print_verbose("pdffonts error on %s. Removing." % pdf_filename)
                os.remove(pdf_filename)
                count += 1
                continue
            # output = subprocess.Popen(["pdffonts", pdf_filename], stdout=subprocess.PIPE).communicate()[0]
            if (len(output.split('\n')) <= 3):
                count += 1
                # this has no fonts and thus is an image.
                scraper_logging.debug_print_verbose("OCR Filtering: " + pdf_filename)
                os.remove(pdf_filename)

    scraper_logging.debug_print("Finished removing %s PDFs that needed OCR." % count)

def filter_encrypted(pdf_dir):
    """
    Remove PDFs that are encrypted, since Acrobat cannot convert them to HTML.
    """
    pattern = re.compile(r"Encrypted:\s*yes", re.U)
    scraper_logging.debug_print("Begin removing PDFs that are encrypted...")
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
                scraper_logging.debug_print_verbose("pdfinfo error on %s. Removing." % pdf_filename)
                os.remove(pdf_filename)
                count += 1
                continue
            # Matching for lines that look like this:
            # Encrypted:      yes (print:yes copy:yes change:no addNotes:no algorithm:RC4)
            if (pattern.search(output)):
                count += 1
                # this has no fonts and thus is an image.
                scraper_logging.debug_print_verbose("Encrypted Filtering: " + pdf_filename)
                os.remove(pdf_filename)

    scraper_logging.debug_print("Finished removing %s PDFs that were encrypted." % count)

def expected_unique_pdfs(csv_dir):
    """
    Count the number of unique datasheet URLs found in the CSV files.
    """
    unique_urls = set()

    for filename in sorted(os.listdir(csv_dir)):
        if filename.endswith(".csv"):
            path = os.path.join(csv_dir, filename)
            scraper_logging.debug_print_verbose('Counting URLs from %s' % path)
            with open(path, 'rb') as csvinput:
                reader = csv.reader(csvinput)
                next(reader, None) # skip the header row
                for row in reader:
                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]

                    # Right now, we will always filter duplicate PDFs.
                    if not (url == '-' or url is None):
                        unique_urls.add(url)
    scraper_logging.debug_print("Expected unique PDFs: %d" % len(unique_urls))

def download_csv(csv_dir, fv_code, pages):
    """
    Scrape the CSV data from the Digikey website for the specified product family.
    """
    data= {
        'fv' : fv_code, # 'ffe002af' for op-amps
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
    scraper_logging.debug_print("Downloading " + str(pages) + " pages...")
    for i in range(pages):
        # Make a bunch of files since each page starts with the CSV header.
        # We don't want random header rows in the CSV file.
        filename = csv_dir + fv_code + "_" + str(i) + ".csv"
        target = open(filename,'w')
        data['page'] = i+1
        r = requests.get('http://www.digikey.com/product-search/download.csv',params=data)
        target.write(r.text.encode('utf-8'))
        target.close()
        scraper_logging.debug_print_verbose("Saved CSV: " + filename)



    # TODO (hchiang): Can we clean up the output of these requests?


def download_pdf(src, dest):
    """
    For each CSV at the 1st level of the src directory, download the datasheet
    and save it to the destination directory.
    """


    total_count = 0

    unique_urls = set()

    for filename in sorted(os.listdir(src)):
        if filename.endswith(".csv"):
            path = os.path.join(src, filename)
            scraper_logging.debug_print('Downloading from %s' % path)
            with open(path, 'rb') as csvinput:
                reader = csv.reader(csvinput)
                next(reader, None) # skip the header row
                for row in reader:
                    # First element of each row is the URL to the PDF
                    url = row[DATASHEET]

                    # Right now, we will always filter duplicate PDFs.
                    if url == '-' or url is None or url in unique_urls:
                        continue

                    # Append 'http:' if none is found in the url. This is because
                    # Digikey sometimes has "//media.digikey.com/..." urls.
                    if not url.startswith("http"):
                        url = "http:" + url

                    try:
                        opener = urllib2.build_opener()
                        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
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

                        basename = re.sub('[^A-Za-z0-9\.\-\_]+', '', basename) # strip away weird characters
                        outfile =  dest + basename # just type the original filename

                        if not (outfile.endswith('.pdf') or outfile.endswith(".PDF")):
                            outfile = outfile + ".pdf"

                        # Lowercase everything to ensure consistency in extensions and remove more duplicates
                        outfile = outfile.lower()

                        scraper_logging.debug_print_verbose("   Saving %s" % outfile)
                        pdf_file = open(outfile, 'w')
                        pdf_file.write(response.read())
                        pdf_file.close()
                        total_count += 1
                    except urllib2.HTTPError, err:
                        if err.code == 404:
                            scraper_logging.debug_print_verbose("    Page not found: %s" % url)
                        elif err.code == 403:
                             # These can mostly be avoided by specifying a user-agent
                             # http://stackoverflow.com/questions/11450649/python-urllib2-cant-get-google-url
                            scraper_logging.debug_print_verbose("    Access Denied: %s" % url)
                        else:
                            scraper_logging.debug_print_verbose("    HTTP Error code %s for %s" % (err.code, url))
                        continue # advance to next datasheet rather than crashing
                    except urllib2.URLError:
                        scraper_logging.debug_print_verbose("    urllib2.URLError for %s" % url)
                        continue
                    except Exception as e:
                        scraper_logging.debug_print_error("Exception %s on URL %s" % (e, url))
                        continue

                    time.sleep(0.1) # Limit our HTTP Requests rate slightly for courtesy.
    scraper_logging.debug_print('Downloaded %d datasheets.' % total_count)

# Main Function
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    scraper_args.parse_args()    # Parse commandline arguments
    start_time = time.time()
    scraper_logging.debug_print('Creating PDF dataset from datasheets in %s' % scraper_args.get_fv_code())

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
    scraper_logging.debug_print('Took ' + str(finish_time - start_time) + ' sec total.')

#! /usr/bin/env python

import sys
import json
import urllib
import urllib2
import time
import argparse
import re

# Category ID for Discrete Semiconductors > Transistors > BJTs
TRANSISTOR_ID = b814751e89ff63d3

def find_total_hits(search_query):
    """
    Function: find_total_hits
    --------------------
    Returns the number of hits that correspond to the search query.
    """
    url = "http://octopart.com/api/v3/categories/"
    # NOTE: Use your API key here (https://octopart.com/api/register)
    url += "?apikey=09b32c6c"
    args = [
        ('q', search_query),
        ('start', 0),
        ('limit', 1), #change to increase number of datasheets
        ('include[]','datasheets')
    ]
    url += '&' + urllib.urlencode(args)

    data = urllib.urlopen(url).read()     # perform a SearchRequest
    search_response = json.loads(data)    # Grab the SearchResponse

    # return number of hits
    return search_response['hits']

def download_datasheets(search_query):
    """
    Function: download_datasheets
    --------------------
    Uses the OctoPart API to download all datasheets associated with a given
    set of search keywords.
    """
    MAX_RESULTS = 100
    counter = 0
    total_hits = find_total_hits(search_query)
    # print number of hits
    print "[info]  Search Response Hits: %s" % (total_hits)

    # Calculate how many multiples of 100s of hits there are
    num_hundreds = total_hits / MAX_RESULTS

    print "[info]  Performing %s iterations of %s results." % (num_hundreds, MAX_RESULTS)
    for i in range(num_hundreds+1):
        url = "http://octopart.com/api/v3/parts/search"
        # NOTE: Use your API key here (https://octopart.com/api/register)
        url += "?apikey=09b32c6c"
        args = [
            ('q', search_query),
            ('start', (i * MAX_RESULTS)),
            ('limit', MAX_RESULTS), # change to edit number of datasheets
            ('include[]','datasheets')
            # ('include[]','specs'),
            # ('include[]','descriptions')
        ]
        url += '&' + urllib.urlencode(args)

        data = urllib.urlopen(url).read()     # perform a SearchRequest
        search_response = json.loads(data)    # Grab the SearchResponse

        # Iterate through the SearchResults in the SearchResponse
        if not search_response.get('results'):
            print "[error] no results returned in outer loop: " + str(i)
            continue
        for result in search_response['results']:
            part = result['item']   # Grab the Part in the SearchResult
            print ("[info]    %s_%s..." % (part['brand']['name'].replace(" ", ""), part['mpn'])),
            sys.stdout.flush()

            # Iterate through list of datasheets for the given part
            for datasheet in part['datasheets']:
                # Grab the Datasheet URL
                pdflink =  datasheet['url']
                if pdflink is not None:
                    # Download the PDF
                    try:
                        response = urllib2.urlopen(pdflink)
                    except urllib2.HTTPError, err:
                        if err.code == 404:
                            print "[error] Page not found!...",
                        elif err.code == 403:
                            print "[error] Access Denied!...",
                        else:
                            print "[error] HTTP Error code ", err.code,
                        continue; # advance to next datasheet rather than crashing
                    try:
                        filename = re.search('([^/]*)\.[^.]*$', datasheet['url']).group(1)
                    except AttributeError:
                        continue; # skip to next datasheet rather than crashing
                    file = open("../datasheets/%s.pdf" % filename, 'w')
                    file.write(response.read())
                    file.close()
                    counter += 1    # Increment the counter of files downloaded

                    # NOTE: Not sure if this is necessary. Just a precaution.
                    time.sleep(0.4) # Limit ourselves to 3 HTTP Requests/second
            print("DONE")
        print("[info]  %s Parts Completed." % MAX_RESULTS)
    print("[info] COMPLETED: %s datasheets for the query were downloaded." % counter)

def parse_args():
    """
    Function: parse_args
    --------------------
    Parse the arguments for the Octopart Datasheet Scraper
    """
    # Define what commandline arguments can be accepted
    parser = argparse.ArgumentParser()
    parser.add_argument('query',metavar="\"SEARCH_KEYWORDS\"",
                        help="keywords to query in quotes (required)")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    args = parser.parse_args()

    return args.query

# Main Function
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    search_query = parse_args()    # Parse commandline arguments
    start_time = time.time()
    print "[info] Download datasheets for %s" % search_query
    download_datasheets(search_query)
    finish_time = time.time()
    print '[info] Took', finish_time - start_time, 'sec total.'

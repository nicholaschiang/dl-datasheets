import json
import urllib
from pprint import pprint

url = "http://octopart.com/api/v3/categories/search"
url += "?apikey=09b32c6c"

args = [
         ('q', 'BJTs'),
         ('start', 0),
         ('limit', 10)
       ]

url += '&' + urllib.urlencode(args)

data = urllib.urlopen(url).read()
search_response = json.loads(data)

# print number of hits
print search_response['hits']

# print results
for result in search_response['results']:
       # print matched category
          pprint(result)

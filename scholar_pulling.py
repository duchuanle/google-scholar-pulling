from lxml.html import fromstring
import requests
from itertools import cycle
import sys
import scholarly
import random

# Name of the input file
filename = "sample.txt"
dictionary = {}
save_path = "/output"

# Obtain the available proxy list on the Internet for proxy rotating
# This is to avoid being blocked by Google for sending requests repetitively
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

with open(filename) as f:
    for line in f:
        dictionary[line] = line

url = 'https://httpbin.org/ip'

# Change language to EN to avoid missing fields in data retrieve due to language mismatch
scholarly.scholarly._PUBSEARCH = '/scholar?hl=en&q={0}'

keywords_count = 0;

# The program will keeps pulling data until keywords count reach desired number
# 50 proxies will be rotate around to pull data
# After 50 proxies have been used up, the code will attempt to pull with a new pool
while keywords_count < 10000:
    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    iterator = 0;

    # Rotate the ip available in the proxy pool
    while iterator < 50:
       proxy = next(proxy_pool)
       print("Request #%d"%iterator)
       try:
          response = requests.get(url,proxies={"http": proxy, "https": proxy})
          print(response.json())

          scholarly.scholarly._SESSION.proxies = {'http' : 'http://' + proxy, 'https' : 'https://' + proxy}
          print(scholarly.scholarly._SESSION.proxies)
          i = 0
          while i < 1000:

              # Select a random word from the target list to pull sample from Google Scholar
              # Then pull result and write a file with the same name as the randomized word

              #random_word = random.choice(list(dictionary.keys()))
              target_word = list(dictionary).pop().keys()
              newFileName = save_path + target_word.replace('\n', '') + ".txt"
              newFile = open(newFileName, "w", encoding="utf-8")
              search_query = scholarly.search_pubs_query(target_word)
              keywords_count = keywords_count + 1
              j = 0
              while j < 100:
                  newFile.write(str(next(search_query)))
                  print(j)
                  sys.stdout.flush()
                  j = j + 1
              newFile.close()
              i = i + 1

       except StopIteration:
           print("Access denied by Google Scholar")
           iterator = iterator + 1
       except:
           print("Skipping. Connnection error")
           iterator = iterator + 1
    print("End of 50 proxy cycle")

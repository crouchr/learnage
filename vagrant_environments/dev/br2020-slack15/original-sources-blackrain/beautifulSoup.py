#!/usr/bin/python

import BeautifulSoup

def extractlinks(html):
    soup = BeautifulSoup.BeautifulSoup(html)
    anchors = soup.findAll('a')
    links = []
    for a in anchors:
        links.append(a['href'])
    return links
    
    
    
html = "<href>http://www.google.com/some-stuff/more-stuff.com</href>"

links = extractlinks(html)
print links

    
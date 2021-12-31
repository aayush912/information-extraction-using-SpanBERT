from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def remove_backslash(line):
    # return repr(line).replace('\\\\','')
    # return re.sub(r"\\",' ',r(line))
    return re.sub("\\'",' ',line)


def scrape_url(url):
    try:
        page = urlopen(url, timeout=30).read()
    except Exception as e:
        return ''

    try:
        bs = BeautifulSoup(page, 'html.parser')
        text = bs.findAll('p')
        text = [p.get_text().replace('\n', '').replace('\t','').replace('\xa0','') for p in text]
        text = [remove_backslash(p) for p in text]
    except Exception as e:
        return ''

    return ' '.join(text) if text else ''

def fetch_content(docs):

    # Scrape a URL and store the content in the dictionary and finally return all URLs that have been processed
    def get_content(d):
        content = scrape_url(d['url'])
        d.update({'content': content})
    for d in docs:
        get_content(d)
    return docs
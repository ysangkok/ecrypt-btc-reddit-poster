import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
strptime = datetime.strptime
import locale
import webbrowser
from urllib.parse import quote

locale.setlocale(locale.LC_ALL, "C")

text = requests.get("https://eprint.iacr.org/eprint-bin/search.pl?keywords=bitcoin").text
soup = BeautifulSoup(text, 'html.parser')

now = datetime.now(timezone.utc)

def calc_diff(date_text):
    day, month, year = date_text.split(" ")
    day, month, year = strptime(day, '%d').date().day, strptime(month, '%b').date().month, strptime(year, '%Y').date().year
    dt = datetime(year, month, day, 0, 0, tzinfo=timezone.utc)
    return now - dt

for line in soup.find_all('dt'):
    identifier = line.a.text
    url = 'https://eprint.iacr.org/{}'.format(identifier)
    url_pdf = url + '.pdf'
    title = line.b.text
    author = line.em.text
    itemtext = requests.get(url).text
    ex = re.compile("<b>Date: </b>received ([A-z0-9 ]+)(, last revised ([A-z0-9 ]+))?<p />")
    res = ex.search(itemtext)
    received_text = res.group(1)
    last_revised = res.group(3)
    if calc_diff(received_text) < timedelta(weeks=4):
        search_result = requests.get("https://old.reddit.com/search", {"q": url_pdf}, headers={"User-Agent": "Mozilla/5.0"})
        if "seen it" in search_result.text:
            continue
        print(url, title, received_text, search_result.status_code)
        webbrowser.open("http://old.reddit.com/r/bitcoin/submit?url={}&title={}".format(quote(url_pdf, safe=''), quote(title, safe='')))
    else:
        break

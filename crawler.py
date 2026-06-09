import requests
from bs4 import BeautifulSoup

URL = "http://placeholder.com"
res = requests.get(URL)
html = res.text
bsoup = BeautifulSoup(html)
for a in bsoup.find_all('a', href=True):
  # code to add a['href'] to tab
  title = str(soup.find('title').string) or None;

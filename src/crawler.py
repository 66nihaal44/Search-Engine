import requests
import re
import nltk
import json
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser
from nltk import PorterStemmer
from sqlalchemy import select
nltk.download('stopwords')
from sqlclass import Page
from engine import engine, SessionLocal
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

user_agent = "MiniCrawler"
robots_websites = {}
stemmer = PorterStemmer() 

def is_valid_url(url):
  parsed = urlsplit(url)
  return (parsed.scheme in ("http", "https") and 
         parsed.netloc and
         "." in parsed.netloc)

def check_robots(site):
  parser_robots = RobotFileParser()
  try:
    parser_robots.set_url(site + "/robots.txt")
    parser_robots.read()
  except Exception as e:
    print("RobotFileParser Error:", e)
  return parser_robots

@sleep_and_retry
@limits(calls=1, period=timedelta(seconds=1).total_seconds())
def crawl(URL, crawled_urls, robots_websites, domain = None, i = 0):
  """if "text" in requests.head(URL).headers['Content-Type']:
    print("True")
  else:
    print("False")
  return
  if URL[-4:] == '.pdf': # implement requests.head() check to avoid scraping binary content
    print("Can't crawl PDF'")
    return"""
  URL = urlsplit(URL)
  if URL.query or URL.fragment:
    print("URL end found:", URL.query, URL.fragment)
  if domain and domain not in URL.netloc.split("."):
    print("Wrong Domain:", URL.netloc, URL.netloc.split("."))
    return
  URL = urlunsplit((
    URL.scheme,
    URL.netloc,
    URL.path,
    "",
    ""
  ))
  if URL in crawled_urls:
    print("ALREADY CRAWLED:", URL)
    return
  crawled_urls.add(URL)
  base_url = urlsplit(URL)
  #base_url = base_url.scheme + "://" + base_url.netloc
  base_url = urlunsplit((
    base_url.scheme,
    base_url.netloc,
    "",
    "",
    ""
  ))
  if base_url not in robots_websites:
    robots_websites[base_url] = check_robots(base_url)
  if not robots_websites[base_url] or not robots_websites[base_url].can_fetch(user_agent, URL):
    print("COULD NOT CRAWL:", URL)
    return
  try:
    res = requests.get(URL, headers={"User-Agent": user_agent})
    if "html" not in res.headers['Content-Type']:
      return
    if res.status_code == 404 or res.status_code == 500:
      print("Response error:", res.status_code)
      return
    html = res.text
  except:
    return
  bsoup = BeautifulSoup(html, "html.parser")
  textsoup = bsoup
  for script in textsoup(["script", "style"]):
    script.decompose()
  textcontent = textsoup.get_text(separator=" ", strip=True)
  textcontent = textcontent.lower()
  textcontent = re.sub(r'\d+', '', textcontent)
  textcontent = re.sub(r'[^\w\s]' ,'', textcontent)
  title = str(bsoup.find('title').string) if bsoup.find('title') else None
  description = str(bsoup.find('meta', name="description").string) if bsoup.find('meta', name="description") else None
  print("title, description: ", title, description)
  # add title and textcontent to sql
  session = SessionLocal()
  try:
    statement = select(Page).filter_by(url=URL)
    exists = session.scalars(statement).first()
    if not exists:
      page = Page(url=URL, title=title, textcontent = textcontent, description = description)
      session.add(page)
      session.commit()
  except Exception as e:
    console.log("Error in SQL session:", e)
    session.rollback()
  finally:
    session.close()
  if i < 3:
    for a in bsoup.find_all('a', href=True):
      # code to add a['href'] to table
      # fix incomplete urls
      if(a['href'] and a['href'][0] == '/'):
        a['href'] = base_url + a['href']
      if is_valid_url(a['href']):
        print(a['href'], '\n')
        crawl(a['href'], crawled_urls, robots_websites, domain, i + 1)

traversed_set = set()
crawl("https://www.niu.edu/index.shtml", traversed_set, robots_websites, "niu")
print('\n', robots_websites)
print("\nTraversed", traversed_set)
"""with open("reverse_index2.txt", "w") as fp:
  json.dump(reverse_index, fp)"""

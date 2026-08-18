from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
from collections import defaultdict
import nltk
from nltk import PorterStemmer
nltk.download('stopwords')
from nltk.corpus import stopwords
from sqlalchemy import select
from sqlclass import Page
from engine import SessionLocal
from ranker import bm25
import os

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))
reverse_index = defaultdict(dict) # index for words and pages
dl = {} # dict of html content lengths
page_titles = {} # dict of page titles
descriptions = {} # dict of meta descriptions

def token_words(words, stemmer, stop_words):
  tokens = [stemmer.stem(word) for word in words]
  tokens = [t for token in tokens if token not in stop_words] # create function words list
  return tokens

def search(query, index):
  query = query.lower()
  query = re.sub(r'\d+', '', query)
  query = re.sub(r'[^\w\s]' ,'', query)
  search_results = defaultdict(int)
  for word in query.split():
    if word not in stop_words:
      stem_word = stemmer.stem(word)
      url_score = bm25(index, stem_word, dl, avdl)
      for url, score in url_score.items():
        search_results[url] += score
      #print("Query term:", stem_word)
      """if stem_word in reverse_index:
        for URL in reverse_index[stem_word]:
          search_results[URL] += reverse_index[stem_word][URL]"""
  #search_results = dict(sorted(search_results.items(), key = lambda x: x[1], reverse = True))
  return search_results

"""with open("reverse_index2.txt", "r") as fp:
  reverse_index = json.load(fp)"""

def add_to_index(URL, textcontent, reverse_index, stop_words):
  for word in textcontent.split():
     if word not in stop_words:
      stem_word = stemmer.stem(word)
      if URL not in reverse_index[stem_word]:
        reverse_index[stem_word][URL] = 1
      else:
        reverse_index[stem_word][URL] += 1

session = SessionLocal()
try:
  statement = select(Page.url, Page.textcontent, Page.title, Page.description)
  page_text = session.execute(statement).all()
  avdl = 0 # track average document length
  for row in page_text:
    page_titles[row[0]] = row[2]
    descriptions[row[0]] = row[3]
    dl[row[0]] = len(row[1]) # add to document length dict
    add_to_index(row[0], row[1], reverse_index, stop_words)
    avdl += len(row[1]) / len(page_text) # avdl
finally:
  session.close()

app = Flask(__name__)
#app.json.sort_keys = False
CORS(app)
@app.route("/search", methods=["POST"])
def search_api():
  data = request.get_json(force=True, silent=False)
  if "query" not in data:
    return # error message here
  query = data["query"]
  query_results = search(query, reverse_index)
  return jsonify({"query_results": query_results, "page_titles": page_titles, "descriptions": descriptions})
if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)

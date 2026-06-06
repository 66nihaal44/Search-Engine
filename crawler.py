import requests

URL = "http://placeholder.com"
res = requests.get(URL)
html = res.content

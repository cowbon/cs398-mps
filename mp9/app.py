import requests
from bs4 import BeautifulSoup
import re
import os
import time
from flask import Flask, render_template, request

app = Flask(__name__)
now = 0
prev_item = ""

@app.route('/', methods=['POST','GET'])
def index():
  global prev_item
  global now
  result = {"answer":0, "time":0}
  if request.method=='POST':
    search_item = {"search": request.form["search"]}
    if search_item["search"] != prev_item:
      now = time.time()
    prev_item = search_item["search"]
    result = search(search_item)
    result["time"] = "{:.2f} seconds".format(time.time() - now)
  return render_template('index.html', count=result)

def search(item):
  result = 0
  url = "https://en.wikipedia.org/wiki/Black_Panther_(film)"

  for i in range(10):
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    url = "https://en.wikipedia.org/%s" % soup.find("a", href=True)['href']
    text = soup.text.lower()

    # YOUR CODE HERE: Find occurences of word here.
    result = text.count(item['search'])
    #result += 0

  return {
    "answer":
    result
  }

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080)

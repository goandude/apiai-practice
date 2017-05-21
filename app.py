#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()
from wikiapi import WikiApi
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
wiki = WikiApi()
wiki = WikiApi({"locale": "en"})  # to specify your locale, 'en' is default

word_list = ["where", "about", "whether", "really"]


@app.route("/webhookquiz", methods=["POST"])
def webhookquiz():
  req = request.get_json(silent=True, force=True)
  print("Request:")
  print(json.dumps(req, indent=4))

  res = quiz(req)

  res = json.dumps(res, indent=4)
  print("Response:")
  print(res)

  r = make_response(res)
  r.headers["Content-Type"] = "application/json"
  return r


def quiz(req):
  result = req.get("result")
  parameters = result.get("parameters")
  game = parameters.get("Game")

  if game == "spelling":
    json_string = play_spelling(req)
  else:
    json_string = play_vocab(req)

  return json_string


def play_spelling(req):
  result = req.get("result")

  word = None
  next_word = None
  for context in result.get("contexts"):
    if context.get("name") == "spell":
      word = context.get("parameters").get("Word")
      break
  print("Word is %s" % (word))

  parameters = result.get("parameters")
  users_word = parameters.get("text")

  if users_word is not None:
    if word == users_word:
      next_word = get_next_word(word)
      result = "Correct! "
      if next_word is not None:
        result += "Spell %s" % next_word
      else:
        result += "No more words to spell"
    else:
      next_word = word
      result = "Not correct. Try again. %s" % next_word

  return {
      "speech":
          result,
      "displayText":
          result,
      "contextOut": [
          {
              "name": "spell",
              "parameters": {
                  "Game.original": "spell",
                  "Game": "spelling",
                  "Word": next_word,
              },
          },
      ],
      "source":
          "apiai-practice"
  }


def get_next_word(current_word):
  for i, word in enumerate(word_list):
    if current_word == word and i < len(word_list) - 1:
      return word_list[i + 1]
  return None


def play_vocab(req):

  return {
      "speech": "Nothing to say",
      "displayText": "Nothing to say",
      "contextOut": [],
      "source": "apiai-practice"
  }


if __name__ == "__main__":
  port = int(os.getenv("PORT", 5000))

  print("Starting app on port %d" % port)

  app.run(debug=False, port=port, host="0.0.0.0")

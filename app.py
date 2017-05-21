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

word_list = ["where", "about", "whether", "really"]


def playing_spelling(req):
  result = req.get("result")
  for context in result.get("contexts"):
    if context.get("name") == "spell":
      return True
  return False


def get_word_just_asked(result):
  word = None
  for context in result.get("contexts"):
    if context.get("name") == "spell":
      word = context.get("parameters").get("Word")
      index = context.get("parameters").get("Index")
      break
  print("DEBUG: Word just asked is %s" % (word))
  return word, index


def get_what_user_said(result):
    parameters = result.get("parameters")
    users_word = parameters.get("any")
    print("DEBUG: User said %s" % (users_word))
    return users_word


def set_word_list(input_text):
  return input_text.lower().split()


def get_next_word(index):
  idx = int(index)
  if idx < len(word_list) - 1:
      idx = idx + 1
      word = word_list[idx]
      index = str(idx)
  else:
    word = None
    index = -1
  print("DEBUG: Next word to spell is %s, index %s" % (word, index))
  return word, index


def play_spelling(req):
  result = req.get("result")

  print("DEBUG: Playing spelling")
  
  word_just_asked, index = get_word_just_asked(result)
  what_to_say_next = "Hmm..."
  
  if word_just_asked is None:
    if not word_list:
      users_word = get_what_user_said(result)
      if "spelling" in users_word:
        what_to_say_next = "What words do you want to spell?"
        next_word = None
        next_index = None
      else:
        set_word_list(users_word)
        next_word = None
        next_index = None
    else:
      next_index = 0
      next_word = word_list[next_index]
      what_to_say_next = "Spell %s" % next_word
  else:  
      users_word = get_what_user_said(result)

      next_word = None
      next_index = None
      if users_word is not None:
        if word_just_asked == users_word:
          what_to_say_next = "Correct! "

          next_word, next_index = get_next_word(index)
          if next_word is not None:
            what_to_say_next += "Spell %s" % next_word
          else:
            what_to_say_next += "Great job, you spelled all of your words!! More spelling or all done?"
        else:
          next_word = word_just_asked
          next_index = index
          what_to_say_next = "Not correct. Try again. %s" % next_word

  return {
      "speech":
          what_to_say_next,
      "displayText":
          what_to_say_next,
      "contextOut": [
          {
              "name": "spell",
              "parameters": {
                  "Word": next_word,
                  "Index": next_index,
              },
          },
      ],
      "source":
          "apiai-practice"
  }


def play_vocab(req):

  return {
      "speech": "Nothing to say",
      "displayText": "Nothing to say",
      "contextOut": [],
      "source": "apiai-practice"
  }

def quiz(req):
  if playing_spelling(req):
    json_string = play_spelling(req)
  else:
    json_string = play_vocab(req)

  return json_string


@app.route("/webhookquiz", methods=["POST"])
def webhookquiz():
  req = request.get_json(silent=True, force=True)
  print("DEBUG: Request:")
  print(json.dumps(req, indent=4))

  res = quiz(req)

  res = json.dumps(res, indent=4)
  print("DEBUG: Response:")
  print(res)

  r = make_response(res)
  r.headers["Content-Type"] = "application/json"
  return r


if __name__ == "__main__":
  port = int(os.getenv("PORT", 5000))

  print("Starting app on port %d" % port)

  app.run(debug=False, port=port, host="0.0.0.0")

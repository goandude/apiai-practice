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

# word_list = ["where", "about", "whether", "really"]
# word_list = []

WHAT_DO_YOU_WANT_TO_SPELL = "Tell me your spelling list. "
RIGHT_ANSWER = "Yep. "
WRONG_ANSWER = "Close. "
TRY_AGAIN = "Try again. "
SPELL_PROMPT = "Spell "
GREAT_JOB = "Great job, you spelled all of your words!! "
EXIT_QUERY = "More spelling, or all done? "
GREAT_JOB='<speak> Good job! <audio src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg">a digital watch alarm</audio> </speak>'

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
      word_list = context.get("parameters").get("WordList")
      break
  print("DEBUG: Word just asked is %s, %s, %s" % (word, index, word_list))
  return word, index, word_list


def get_what_user_said(result):
  users_word = result.get("resolvedQuery")

  if users_word:
      users_word = users_word.lower()
  return users_word
  

def set_word_list(input_text):
  return input_text.lower().split()


def get_next_word(index, word_list):
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
  
  word_just_asked, index, word_list = get_word_just_asked(result)
  if word_list:
    word_list = word_list.split()
  what_to_say_next = "Hmm..."
  
  if not word_list:
      users_word = get_what_user_said(result)
      if "spell" in users_word:
        what_to_say_next = WHAT_DO_YOU_WANT_TO_SPELL
        next_word = None
        next_index = None
      else:
        word_list = set_word_list(users_word)
        print("DEBUG: Set word list to " , word_list)
        next_index = 0
        next_word = word_list[next_index]
        what_to_say_next = "%s %s" % (SPELL_PROMPT, next_word)
  else:    
      users_word = get_what_user_said(result)
      next_word = None
      next_index = None
      if users_word is not None:
        if word_just_asked == users_word:
          what_to_say_next = RIGHT_ANSWER

          next_word, next_index = get_next_word(index, word_list)
          if next_word is not None:
            what_to_say_next += "%s %s" % (SPELL_PROMPT, next_word)
          else:
            what_to_say_next += GREAT_JOB + EXIT_QUERY
        else:
          next_word = word_just_asked
          next_index = index
          what_to_say_next = "%s. %s. %s. %s." % (WRONG_ANSWER, ", ".join(next_word), TRY_AGAIN, next_word)

  next_word_list = None
  if word_list is not None:
    next_word_list = " ".join(word_list)     
          
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
                  "WordList": next_word_list,
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

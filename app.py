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
wiki = WikiApi({ 'locale' : 'en'}) # to specify your locale, 'en' is default

@app.route('/webhookquiz', methods=['POST'])

word_list = ['where', 'about', 'whether', 'really']

def webhookquiz():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    
    res = quiz(req)

    res = json.dumps(res, indent=4)
    print("Response:")
    print(res)

    r = make_response(res)    
    r.headers['Content-Type'] = 'application/json'
    return r


def quiz(request):
    result = request.get("result")
    parameters = result.get("parameters")
    query = parameters.get("text")
    
    contexts = result.get("contexts")
    quizword = contexts[0].get("name")
    
    print("query is ")
    print(query)
    print("quizword is ")
    print(quizword)
    
    if query == quizword : 
        result = "That is absolutely correct"
    else:
        result = "That is wrong. It is spelt C A T"
    #results = wiki.find(query) 
    #article = wiki.get_article(results[0])
    #result = article.content 
    #result1 = duckduckgo.get_zci(query)
    
    return {
        "speech": result,
        "displayText": query,
     #   "data": result1,
         "contextOut": [],
        "source": "apiai-weather-webh29ook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

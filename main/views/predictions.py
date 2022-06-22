import json
import sys
from datetime import datetime

import dill as pickle
import gensim
import nltk
import numpy as np
import pandas as pd
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError, send_mail
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from main.forms import ContactForm, NewUserForm, VideoForm, ReviewForm
from main.models import Stmt
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from tensorflow import keras
from tensorflow.keras.models import load_model
from youtube_transcript_api import YouTubeTranscriptApi

from googleapiclient.discovery import build

from main.models import Review

def getVideo(request):
    form = VideoForm(auto_id=False)
    review_form = ReviewForm(auto_id=False)
    if request.method == "POST":
        form = VideoForm(request.POST, auto_id=False)
        print("\n\n\n")
        print(form)
        print("\n\n\n")
        # claimReviewForm = ReviewForm(request.POST, auto_id=False)
        if form.is_valid():
            print(form.cleaned_data['video_url'])
    return render(request, 'main/video.html', context={'url': form.cleaned_data['video_url'], 'review_form': review_form})

# Assuming claims is a list of claims, we predict on it
def predictData(claims, use_mean = False):
  # for claims in claim_data:
    df = pd.DataFrame([claims], columns = ['data'])
    df.data = df.data.transform(gensim.parsing.preprocessing.preprocess_string)
    tokenizer = pickle.load(open('classifier/tokenizer.pkl', 'rb'))
    model = load_model('classifier/classifier.h5')
    # k_max_sequence_len = 1500
    k_max_sequence_len = 224*224*3
    pdata = keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences(df.data), maxlen = k_max_sequence_len)

    print("\n\n\n<======================>")
    print("pdata:")
    print(len(pdata[0]))
    print("\n\n\n<======================>")
    pdata=pdata.reshape(1,224,224,3)
    ypred = model.predict(pdata) # Error in this line
    ypred = ypred.reshape(len(ypred[0]))
    probs = ypred.round(4)
    #cutoff = np.mean(ypred) # change this after adding google scraping
    # if use_mean:
    #     cutoff = np.mean(ypred)
    # else:
    #     # cutoff = 0.5
    cutoff=0.0005
    # res = ypred > cutoff 
    res=probs>cutoff
    res = np.array(res, dtype = bool)
    if res[0] and res[1]:
      res = ['True']
    else:
      res = ['False']
    return res, probs
    

# H
def generate_claims(request):
  try:
    video_id = request.POST['id']
    print(video_id)
    tdict = YouTubeTranscriptApi.get_transcript(video_id)
    print(tdict)
    api_key = "b033571c3e114464b2c82f0d3e5bb132"

    sentences = []
    j = 0
    t = ""
    for i in tdict:
      if (j == 3):
        sentences.append(t)
        j = 0
        t = ""
      t = t + " " + i['text']
      j+=1

    sentences = [x.replace('\n',' ') for x in sentences]
    tdict_txts = '\n'.join(sentences)

    # api_endpoint = f"https://idir.uta.edu/claimbuster/api/v2/score/paragraphs/"
    # request_headers = {"x-api-key": api_key}
    # payload = {"input_text": tdict_txts, "delimiter":'\n'}

    # # Send the GET request to the API and store the api response
    # api_response = requests.post(url=api_endpoint, json=payload, headers=request_headers)


    api_endpoint = "https://idir.uta.edu/claimbuster/api/v2/score/text/"
    request_headers = {"x-api-key": api_key}
    payload = {"input_text": tdict_txts}

    # Send the POST request to the API and store the api response
    api_response = requests.post(url=api_endpoint, json=payload, headers=request_headers)

    # print out the JSON payload the API sent back
    sent_ls = []
    for res in api_response.json()['results']:
      
      # for item in res:
      sent_ls.append([res['text'],res['score']])

    # sent_ls = [x[0] for x in sent_ls if x[1] > 0.5]
    sent_ls = [x[0] for x in sent_ls]

    final_claim_ls = []
    for capt in tdict:
      for ranked in sent_ls:
        if capt['text'] in ranked and len(capt['text'].split(' ')) >= 3:
          final_claim_ls.append({'claim':ranked, 'start':capt['start'], 'duration':capt['duration'], 'status': '', 'probability':0})
    
    # remove duplicate claims
    done = set()
    rem_dup = []
    for d in final_claim_ls:
      if d['claim'] not in done:
        done.add(d['claim']) 
        rem_dup.append(d)
    final_claim_ls = rem_dup


    # ================For using pre-saved data latest code
    # final_result = []
    # final_prob = []
    # loaded=False
    # with open('classifier/claim.pkl', 'rb') as f:
    #   claim_data = pickle.load(f)
    # with open('classifier/final_ls.pkl', 'rb') as f:
    #   final_claim_ls = pickle.load(f)
    # final_claim_ls = final_claim_ls[:5]
    # done = set()
    # rem_dup = []
    # for d in final_claim_ls:
    #   if d['claim'] not in done:
    #     done.add(d['claim']) 
    #     rem_dup.append(d)
    # final_claim_ls = rem_dup
    # claim_data = []
    # for x in final_claim_ls:
    #   claim_data.append(x['claim'])
    # for claims in claim_data:
    #   result, prob = predictData(claims, True)
    #   final_result.append(result)
    #   final_prob.append(prob)
    # result = final_result
    # prob = final_prob
    # raw_claim_data = [sub['claim'] for sub in final_claim_ls]
    # db_status, db_prob, db_data = check_database(raw_claim_data)

    #==================== using saved data 
    # loaded = False
    # with open('classifier/claim.pkl', 'rb') as f:
    #   claim_data = pickle.load(f)
    # with open('classifier/final_ls.pkl', 'rb') as f:
    #   final_claim_ls = pickle.load(f)
    # done = set()
    # rem_dup = []
    # for d in final_claim_ls:
    #   if d['claim'] not in done:
    #     done.add(d['claim']) 
    #     rem_dup.append(d)
    # final_claim_ls = rem_dup
    # final_claim_ls=[final_claim_ls[0],final_claim_ls[1]]
    # for x in final_claim_ls:
    #   claim_data = [sub['claim'] for sub in [x]]
    # result, prob = predictData(claim_data, use_mean = True)
    # raw_claim_data = [sub['claim'] for sub in final_claim_ls]
    # db_status, db_prob, db_data = check_database(raw_claim_data)

    # TODO: uncomment to switch to google snippets
    # claim_data = [get_claim_and_snippet(sub['claim']) for sub in final_claim_ls]
    # if video_id == 'zDbK0IpNTmM':
    #   print('Using cached search data!')
    #   loaded = True
    #   with open('classifier/claim.pkl', 'rb') as f:
    #     claim_data = pickle.load(f)
    #   with open('classifier/final_ls.pkl', 'rb') as f:
    #     final_claim_ls = pickle.load(f)
    #   print(len(claim_data), len(final_claim_ls))
    #   result, prob = predictData(claim_data)
    #   raw_claim_data = [sub['claim'] for sub in final_claim_ls]
    #   db_status, db_prob, db_data = check_database(raw_claim_data)
    # else:
    #     loaded = False
    #     claim_data = [sub['claim'] for sub in final_claim_ls]
    #     result, prob = predictData(claim_data, use_mean = True)
    #     db_status, db_prob, db_data = check_database(claim_data)

    
    

    # ===============uncomment if using api response data
    final_result = []
    final_prob = []
    loaded=False
    claim_data = [sub['claim'] for sub in final_claim_ls]
    for claims in claim_data:
      result, prob = predictData(claims, False)
      final_result.append(result)
      final_prob.append(prob)
    result = final_result
    prob = final_prob
    raw_claim_data = [sub['claim'] for sub in final_claim_ls]
    db_status, db_prob, db_data = check_database(raw_claim_data)
    
    # I need: db_status, db_prob, and db = list of dictionaries, each having status, reason
    

    for i in range(len(final_claim_ls)):
      final_claim_ls[i]['status'] = result[i]
      p = prob[i][0] if result[i] == 'True' else 1 - prob[i][0]
      if not loaded:
        p = 1-p if p < 0.5 else p
      final_claim_ls[i]['probability'] = str(round(100 * p, 2))
      final_claim_ls[i]['db_status'] = db_status[i]
      final_claim_ls[i]['db_prob'] = str(100*db_prob[i])
      final_claim_ls[i]['db_data'] = db_data[i]

    # sort claims by start
    final_claim_ls = sorted(final_claim_ls, key=lambda k: k['start'])
    y = json.dumps(final_claim_ls)
    return HttpResponse(y, content_type="application/json")
  except Exception as e:
    print('error:::',e)
    return JsonResponse({'message': 'Subtitles are disabled for this video'}, status=500) 



def google_search(search_term,  **kwargs):
    api_key = "AIzaSyBMqcM3WTnJbD02xBYkZO_6seCwlz_nUGA"
    cse_id = "4086bbbf30a4ac715"
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

def get_claim_and_snippet(claim):

    res = google_search(claim)
    snippets = ""
    tab = "\t"
    for i, snippet  in enumerate(res['items']):
        snippets = snippets + str(i + 1) + tab + snippet['title'] + tab + snippet['snippet'] + "\n"
    data = claim + tab+ snippets
    return data

def check_database(claims):
    cutoff = 0.5
    db_status = []
    db_prob = []
    db = []
    for claim in claims:
        print(claim)
        query = Review.objects.filter(claim_text__contains = claim).values('claim_status', 'claim_reason')
        if query:
            true_p = round(query.filter(claim_status = 'True').count() / query.count(),2)
            print(true_p)
            if true_p > cutoff:
                db_status.append('True')
                db_prob.append(true_p)
            else:
                db_status.append('False')
                db_prob.append(1-true_p)
            db.append(list(query))
        else:
            db_status.append('None')
            db_prob.append(-1)
            db.append(None)

    print(db_status)
    print(db_prob)
    print(db)
    return db_status, db_prob, db

@api_view(['POST'])
def result_view(request):
  data = JSONParser().parse(request)
  sentences = data['sentences']
  result, prob = predictData(sentences)
  return_ls = []
  for i in range(len(sentences)):
    p = prob[i][0] if result[i] == 'True' else 1 - prob[i][0]
    return_ls.append({'claim':sentences[i] ,'class':result[i], 'probability':str(round(100 * p, 2))})      
  return HttpResponse(json.dumps(return_ls), content_type="application/json")

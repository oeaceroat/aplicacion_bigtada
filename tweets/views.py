import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render

import re

import paramiko
from urllib.parse import urlparse
import http.client
from scp import SCPClient
import json
from lxml import etree
import os, sys
import networkx as nx


from django.conf import settings


import pymongo
from pymongo import MongoClient

def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'tweets/index.html', context)


def getPolaridad(request):

    try:
        #client = MongoClient('127.0.0.1', 27017)
        # db = client.taller3 #local

        client = MongoClient('bigdata-mongodb-01', 27017)#Produccion
        db = client.Grupo01_Taller3 #Produccion

        print(db.collection_names())
        collection = db.tweets_tema

        tweets = collection.find().limit(30)

        data = []

        for doc in tweets:
            tweet = {
                "hashtag": "holamundo",
                "full_text": doc["full_text"],
                "tema": doc["tema"],
                "clase": doc["clase"]
            }
            data.append(tweet)

    except Exception as e:
        print(str(e))

    response_data = {}
    response_data["data"] = data

    return JsonResponse(response_data)
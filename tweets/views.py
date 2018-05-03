import base64
import matplotlib
from cycler import concat

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
import pandas as pd


def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'tweets/index.html', context)


def getPolaridad(request):

    #try:
    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller3 #local

    client = MongoClient('bigdata-mongodb-01', 27017)#Produccion
    db = client.Grupo01_Taller3 #Produccion

    #print(db.collection_names())
    collection = db.tweets_tema

    tweets = collection.find({"$and": [
        {"clase": {"$exists":True}}, {"retweeted_status":{"$exists":False}}]
    }).limit(1000).sort('retweet_count', -1)

    data = []
    i=0
    for doc in tweets:
        i+=1
        #print(i)
        hastags = doc["entities"]["hashtags"]
        concat = ""
        #print(hastags)
        if(len(hastags) > 0):
            cont = 0
            for ht in hastags:
                cont += 1
                if cont == len(hastags):
                    concat = concat + ht["text"]
                else:
                    concat = concat + ht["text"] + "," + "\n"


        tweet = {
            "hashtag": concat,
            "full_text": doc["full_text"],
            "tema": doc["tema"],
            "clase": doc["clase"]
        }
        data.append(tweet)

    #except Exception as e:
    #    print(str(e))

    response_data = {}
    response_data["data"] = data

    return JsonResponse(response_data)


def busquedaPorScreenFecha_h(screen, mes, año):

    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller3  # local

    client = MongoClient('bigdata-mongodb-01', 27017)#Produccion
    db = client.Grupo01_Taller3 #Produccion

    resp = []

    meses = {"": "", 'Enero': 'Jan', 'Febrero': 'Feb', 'Marzo': 'Mar', 'Abril': 'Apr', 'Mayo': 'May', 'Junio': 'Jun',
             'Julio': 'Jul', 'Agosto': 'Aug', 'Septiembre': 'Sep', 'Octubre': 'Oct', 'Noviembre': 'Nov',
             'Diciembre': 'Dec'}


    # pat = re.compile(inicio[0], re.I)
    # cur=db.tweets.find({"$and": [{ "created_at": {'$regex': meses[mes]}},{ "created_at": {'$regex': año}}]})
    cur = db.tweets.find({"$and": [{"user.screen_name": {"$regex": screen}},
                                   {"created_at": {'$regex': meses[mes]}}, {"created_at": {'$regex': año}}]})

    for item in cur:
        temporal = {}
        try:
            temporal['screen_name'] = item['user']['screen_name']
            temporal['name'] = item['user']['name']
            temporal['full_text'] = item['full_text']
            temporal['created_at'] = item['created_at']
        except:
            pass;
        temporal['user_favourites_count'] = item['user']['favourites_count']
        temporal['tweet_favourites_count'] = item['favorite_count']
        temporal['followers_count'] = item['user']['followers_count']
        temporal['user_mentions'] = ""
        temporal['hashtags'] = ""
        for i in item['entities']['user_mentions']:
            temporal['user_mentions'] += i['name'] + "(@" + i['screen_name'] + ") "
        for j in item['entities']['hashtags']:
            temporal['hashtags'] += "#" + j['text'] + " "
        if "RT" in item['full_text']:
            temporal['esRetweet'] = "1"
        else:
            temporal['esRetweet'] = "0"
        try:
            temporal['retweet_nombre'] = item['retweeted_status']['user']['name']
            temporal['retweet_screen_name'] = item['retweeted_status']['user']['screen_name']
        except:
            pass;
        resp.append(temporal)
    return resp



def getEvolucion(request):

    client = MongoClient('127.0.0.1', 27017)
    db = client.taller3  # local

    # client = MongoClient('bigdata-mongodb-01', 27017)#Produccion
    # db = client.Grupo01_Taller3 #Produccion

    ruta_base = settings.BASE_DIR + '/tweets/static/tweets/'

    candidatos = ['petrogustavo', 'sergio_fajardo', 'IvanDuque', 'DeLaCalleHum', 'German_Vargas']
    for screen in candidatos:
        wer = pd.DataFrame(busquedaPorScreenFecha_h(screen, "Abril", "2018"))
        wer['fecha'] = wer['created_at'].apply(
            lambda x: x.split(' ')[1] + " " + x.split(' ')[2] + " " + x.split(' ')[-1])
        wer['mes'] = wer['created_at'].apply(lambda x: x.split(' ')[1])
        plt.plot(wer.groupby('fecha')['user_favourites_count'].mean())
        plt.xticks(rotation=90)
        titulo_1 = "Favoritos @" + screen
        plt.title(titulo_1)
        plt.savefig(ruta_base + screen + 'Favoritos.png', dpi=100, bbox_inches='tight')
        plt.close()
        plt.plot(wer.groupby('fecha')['followers_count'].mean())
        plt.xticks(rotation=90)
        titulo_2 = "Seguidores @" + screen
        plt.title(titulo_2)
        plt.savefig(ruta_base + screen + 'Seguidores.png', dpi=100, bbox_inches='tight')
        plt.close()



    response_data = {}

    return JsonResponse(response_data)




def busquedaPorFecha(request, dia, mes, anio):

    año = anio
    client = MongoClient('127.0.0.1', 27017)
    db = client.taller3  # local

    # client = MongoClient('bigdata-mongodb-01', 27017)#Produccion
    # db = client.Grupo01_Taller3 #Produccion

    resp = []

    meses = {"": "", 'Enero': 'Jan', 'Febrero': 'Feb', 'Marzo': 'Mar', 'Abril': 'Apr', 'Mayo': 'May', 'Junio': 'Jun',
             'Julio': 'Jul', 'Agosto': 'Aug', 'Septiembre': 'Sep', 'Octubre': 'Oct', 'Noviembre': 'Nov',
             'Diciembre': 'Dec'}
    # pat = re.compile(inicio[0], re.I)
    cur = db.tweets_tema.find({"$and": [{"created_at": {'$regex': dia}}, {"created_at": {'$regex': meses[mes]}},
                                   {"created_at": {'$regex': año}}]}).limit(10)
    for item in cur:
        temporal = {}
        try:
            temporal['screen_name'] = item['user']['screen_name']
            temporal['name'] = item['user']['name']
            temporal['full_text'] = item['full_text']
            temporal['created_at'] = item['created_at']
        except:
            pass;
        temporal['user_favourites_count'] = item['user']['favourites_count']
        temporal['tweet_favourites_count'] = item['favorite_count']
        temporal['followers_count'] = item['user']['followers_count']
        temporal['user_mentions'] = ""
        temporal['hashtags'] = ""
        for i in item['entities']['user_mentions']:
            temporal['user_mentions'] += i['name'] + "(@" + i['screen_name'] + ") "
        for j in item['entities']['hashtags']:
            temporal['hashtags'] += "#" + j['text'] + " "
        if "RT" in item['full_text']:
            temporal['esRetweet'] = "Sí"
        else:
            temporal['esRetweet'] = "No"
        try:
            temporal['retweet_nombre'] = item['retweeted_status']['user']['name']
            temporal['retweet_screen_name'] = item['retweeted_status']['user']['screen_name']
        except:
            pass;

        resp.append(temporal)

    responde_data = {}
    responde_data["data"] = resp
    return JsonResponse(responde_data, safe=False)


def busquedaPorScreenFecha(request, screen, mes, anio):
    año = anio
    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller3  # local

    client = MongoClient('bigdata-mongodb-01', 27017)  # Produccion
    db = client.Grupo01_Taller3  # Produccion

    resp = []

    meses = {"": "", 'Enero': 'Jan', 'Febrero': 'Feb', 'Marzo': 'Mar', 'Abril': 'Apr', 'Mayo': 'May', 'Junio': 'Jun',
             'Julio': 'Jul', 'Agosto': 'Aug', 'Septiembre': 'Sep', 'Octubre': 'Oct', 'Noviembre': 'Nov',
             'Diciembre': 'Dec'}
    # pat = re.compile(inicio[0], re.I)
    # cur=db.tweets.find({"$and": [{ "created_at": {'$regex': meses[mes]}},{ "created_at": {'$regex': año}}]})
    cur = db.tweets.find({"$and": [{"user.screen_name": {"$regex": screen}},
                                   {"created_at": {'$regex': meses[mes]}}, {"created_at": {'$regex': año}}]})
    print(cur.count())
    for item in cur:
        temporal = {}
        try:
            temporal['screen_name'] = item['user']['screen_name']
            temporal['name'] = item['user']['name']
            temporal['full_text'] = item['full_text']
            temporal['created_at'] = item['created_at']
        except:
            pass;
        temporal['user_favourites_count'] = item['user']['favourites_count']
        temporal['tweet_favourites_count'] = item['favorite_count']
        temporal['followers_count'] = item['user']['followers_count']
        temporal['user_mentions'] = ""
        temporal['hashtags'] = ""
        for i in item['entities']['user_mentions']:
            temporal['user_mentions'] += i['name'] + "(@" + i['screen_name'] + ") "
        for j in item['entities']['hashtags']:
            temporal['hashtags'] += "#" + j['text'] + " "
        if "RT" in item['full_text']:
            temporal['esRetweet'] = "1"
        else:
            temporal['esRetweet'] = "0"
        try:
            temporal['retweet_nombre'] = item['retweeted_status']['user']['name']
            temporal['retweet_screen_name'] = item['retweeted_status']['user']['screen_name']
        except:
            pass;
        print(temporal)
        resp.append(temporal)

    responde_data = {}
    responde_data["data"] = resp
    return JsonResponse(responde_data, safe=False)




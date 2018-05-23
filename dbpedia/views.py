from django.shortcuts import render

import io
from django.http import HttpResponse, JsonResponse
from pymongo import MongoClient
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

from SPARQLWrapper import SPARQLWrapper, JSON
import pprint

import textrazor


# Create your views here.

def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'dbpedia/index.html', context)

def getQuestions(request):


    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller4  # Local

    client = MongoClient('bigdata-mongodb-01', 27017)  # Produccion
    db = client.Grupo01_Taller4  # Produccion


    obj = {}
    data = []
    cursor_questions = db.questions.find({}).limit(1000)

    for q in cursor_questions:

        obj = {}
        obj["question_title"] = q["body"]
        cursor_answers = db.answers.find({"question_id": q["question_id"]}).limit(1000)

        text = ""
        i = 1
        for a in cursor_answers:

            aux = str(i) + ") " + a["body"] + "\n"
            text += aux
            i += 1
        obj["answers"] = text
        data.append(obj)

    response_data = {}
    response_data["data"] = data
    return JsonResponse(response_data)


def getMusicalArtists(request):

    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller4  # Local

    client = MongoClient('bigdata-mongodb-01', 27017)  # Produccion
    db = client.Grupo01_Taller4  # Produccion


    cursor = db.entities.find({"dbpedia_types": {"$in": ["MusicalArtist"]}}).limit(1000)

    obj = {}
    data = []
    response_data = {}
    for entidad in cursor:
        print(entidad["id"])

        obj = {}
        obj["id"] = entidad["id"]

        try:
            obj["birthDate"] = entidad["data"]["birthDate"]["value"]
        except Exception as e:
            obj["birthDate"] = "-"

        try:
            obj["deathDate"] = entidad["data"]["deathDate"]["value"]
        except Exception as e:
            obj["deathDate"] = "-"

        try:
            obj["residence_name"] = entidad["data"]["residence_name"]["value"]
        except Exception as e:
            obj["residence_name"] = "-"
        try:
            obj["birthPlace"] = entidad["data"]["birthPlace_name"]["value"]
        except Exception as e:
            obj["birthPlace"] = "-"
        try:
            obj["genre"] = entidad["data"]["genre_name"]["value"]
        except Exception as e:
            obj["genre"] = "-"

        data.append(obj)

    response_data["data"] = data
    return JsonResponse(response_data)

def getPlaces(request):
    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller4  # Local

    client = MongoClient('bigdata-mongodb-01', 27017)  # Produccion
    db = client.Grupo01_Taller4  # Produccion

    cursor = db.entities.find({"dbpedia_types": {"$in": ["Place"]}}).limit(1000)

    obj = {}
    data = []
    response_data = {}
    for entidad in cursor:
        print(entidad["id"])

        obj = {}
        obj["id"] = entidad["id"]

        try:
            obj["point"] = entidad["data"]["point"]["value"]
        except Exception as e:
            obj["point"] = "-"

        try:
            obj["name_location"] = entidad["data"]["name_location"]["value"]
        except Exception as e:
            obj["name_location"] = "-"
        try:
            obj["name_partOf"] = entidad["data"]["name_partOf"]["value"]
        except Exception as e:
            obj["name_partOf"] = "-"
        try:
            obj["name_country"] = entidad["data"]["name_country"]["value"]
        except Exception as e:
            obj["name_country"] = "-"

        data.append(obj)

    response_data["data"] = data
    return JsonResponse(response_data)

def getSongs(request):

    # client = MongoClient('127.0.0.1', 27017)
    # db = client.taller4  # Local

    client = MongoClient('bigdata-mongodb-01', 27017)  # Produccion
    db = client.Grupo01_Taller4  # Produccion

    cursor = db.entities.find({"dbpedia_types": {"$in": ["Song"]}}).limit(1000)

    obj = {}
    data = []
    response_data = {}
    for entidad in cursor:
        print(entidad["id"])

        obj = {}
        obj["id"] = entidad["id"]

        try:
            obj["popularity"] = entidad["data"]["popularity"]
        except Exception as e:
            obj["popularity"] = "-"

        try:
            obj["duration_ms"] = entidad["data"]["duration_ms"]
        except Exception as e:
            obj["duration_ms"] = "-"

        try:
            obj["album"] = entidad["data"]["album"]
        except Exception as e:
            obj["album"] = "-"

        try:
            obj["artist"] = entidad["data"]["artist"]
        except Exception as e:
            obj["artist"] = "-"

        try:
            obj["release_date"] = entidad["data"]["release_date"]
        except Exception as e:
            obj["release_date"] = "-"

        data.append(obj)

    response_data["data"] = data
    return JsonResponse(response_data)

def runEnrich(request):

    #client = MongoClient('127.0.0.1', 27017)
    #db = client.taller4 #Local

    client = MongoClient('bigdata-mongodb-01', 27017)  # Produccion
    db = client.Grupo01_Taller4  # Produccion

    entities = db.entities.find()

    for e in entities:
        enrichEntity(e, db)

    #cursor = db.entities.find({"data": {"$exists": True}}).limit(1000)

    response_data = {}
    data = "Enriquecimiento OK"
    response_data["data"] = data
    #for obj in cursor:
    #    data["entidad"] = obj["id"]
    #   data["tipos"] = obj["dbpedia_types"]

    return JsonResponse(response_data)

def enrichEntity(entity, db):

    type_dp = ""
    data = {}

    if 'MusicalArtist' in entity["dbpedia_types"]:
        type_dp = "MusicalArtist"

    elif 'Song' in entity["dbpedia_types"]:
        type_dp = "Song"

    elif 'Place' in entity["dbpedia_types"]:
        type_dp = "Place"

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    if type_dp == "MusicalArtist":
        # Enriquece persona
        '''
        sparql.setQuery("""
            PREFIX dbo: <http://dbpedia.org/ontology/> 
            PREFIX dbp: <http://dbpedia.org/property/> 
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT ?birthDate ?residence ?birthPlace ?genre   
            WHERE {
                 ?person foaf:name """ + "'" + entity["id"] + "'" + """@en.
                 OPTIONAL {?person dbo:birthDate ?birthDate;
                 dbo:birthDate ?birthDate}
                 OPTIONAL {?person dbo:birthPlace ?birthPlace;
                 dbo:birthPlace ?birthPlace}
                 OPTIONAL {?person dbo:genre ?genre;
                 dbo:genre ?genre}
                 OPTIONAL {?person dbo:residence ?residence;
                 dbo:residence ?residence}

             }
        """)
        
        '''

        sparql.setQuery("""
                    PREFIX dbo: <http://dbpedia.org/ontology/> 
                    PREFIX dbp: <http://dbpedia.org/property/> 
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?birthDate ?deathDate ?residence_name ?birthPlace_name ?genre_name   
                    WHERE {
                         ?person foaf:name """ + "'" + entity["id"] + "'" + """@en.
                         OPTIONAL {?person dbo:birthDate ?birthDate;
                         dbo:birthDate ?birthDate}
                          OPTIONAL {?person dbo:deathDate ?deathDate;
                         dbo:deathDate ?deathDate}
                         OPTIONAL {?person dbo:birthPlace ?birthPlace.
                         ?birthPlace foaf:name ?birthPlace_name}
                         OPTIONAL {?person dbo:genre ?genre.
                         ?genre foaf:name ?genre_name}
                         OPTIONAL {?person dbo:residence ?residence.
                         ?residence foaf:name ?residence_name}

                     }
                """)


        try:
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            data = results['results']['bindings'][0]
        except Exception as e:
            print(str(e))

    elif type_dp == "Place":
        # Enriquece lugar
        sparql.setQuery("""
            PREFIX dbo: <http://dbpedia.org/ontology/> 
            PREFIX dbp: <http://dbpedia.org/property/> 
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX georss: <http://www.georss.org/georss/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            SELECT ?point ?name_location ?name_partOf ?name_country
            WHERE {
                 ?place rdfs:label """ + "'" + entity["id"] + "'" + """@en.
                 OPTIONAL {?place georss:point ?point;
                 georss:point ?point}
                 OPTIONAL {?place dbo:location ?location.
                    ?location foaf:name ?name_location.
                    ?location dbo:isPartOf ?isPartOf.
                    ?isPartOf foaf:name ?name_partOf.
                    ?isPartOf dbo:country ?country.
                    ?country foaf:name ?name_country}

             }
        """)
        try:
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            data = results['results']['bindings'][0]
        except Exception as e:
            print(str(e))

    elif type_dp == "Song":
        data = enrichSong(entity["id"])

    try:
        db.entities.update_one(
            {'id': entity["id"]},
            {'$set': {"data": data}})
        print("Entidad " + entity["id"] + " enriquecida")

    except Exception as e:
        print(str(e))

def enrichSong(song_name):
    client_id = "d080ad9e5c084c548d9efd181f662487"
    client_secret = "01dd6d626a6a4bd2ace9f4ede5b1cf7b"
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q=song_name, type=["track"], limit=1)

    data = {}
    for i, t in enumerate(results['tracks']['items']):
        data['popularity'] = t['popularity']
        data['duration_ms'] = t['duration_ms'] / 60000
        data['album'] = t['album']['name']
        data['artist'] = t['album']['artists'][0]['name']
        data['release_date'] = t['album']['release_date']

    return data


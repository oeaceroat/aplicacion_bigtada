from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import re

import feedparser
import json
from lxml import etree
import os, sys

def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'rss_feed/index.html', context)


#Para filtro con xquery

def xQuery_data(feed_url_XQ, filter_option, key ):
    ## Consulta de fuentes de sindicación/suscripción a través de XQuery:
    ## para llevar a cabo esta actividad se usa la libreria lxml

    feed_list_XQ = []
    feed_id_XQ = 0

    for url_XQ in feed_url_XQ:
        #       parsed_feed = feedparser.parse(feed_url_XQ)
        print(url_XQ)

        try:

            XQuery_feed = etree.parse(url_XQ)
            Titulo_xq = etree.XPath("//title")
            Link_xq = etree.XPath("//link")
            FecPub_xq = etree.XPath("//pubDate")

            for x in range(0, len(Titulo_xq(XQuery_feed))):

                nombre_tit = Titulo_xq(XQuery_feed)[x].text
                v_descripcion = Link_xq(XQuery_feed)[x].text
                #v_fecpub = FecPub_xq(XQuery_feed)[x].text

                v_xquery = ".*" + key + ".*"

                if filter_option == 'title' and re.match(v_xquery, nombre_tit):
                    feed_id_XQ += 1
                    feed_XQ = {"feed_id": feed_id_XQ,
                               "feed_title": str(Titulo_xq(XQuery_feed)[x].text),
                               "feed_link": str(Link_xq(XQuery_feed)[x].text),
                               "feed_Fecp": str(FecPub_xq(XQuery_feed)[x].text)}
                    feed_list_XQ.append(feed_XQ)
                elif filter_option == 'description' and re.match(v_xquery, v_descripcion):
                    feed_id_XQ += 1
                    feed_XQ = {"feed_id": feed_id_XQ,
                               "feed_title": str(Titulo_xq(XQuery_feed)[x].text),
                               "feed_link": str(Link_xq(XQuery_feed)[x].text),
                               "feed_Fecp": str(FecPub_xq(XQuery_feed)[x].text)}
                    feed_list_XQ.append(feed_XQ)
                    '''
                   elif filter_option == 'category' and re.match(v_xquery, v_fecpub):
                       feed_id_XQ += 1
                                       feed_XQ = {"feed_id": feed_id_XQ, "feed_title": str(Titulo_xq(XQuery_feed)[feed_id_XQ].text), "feed_link": str(Link_xq     (XQuery_feed)[feed_id_XQ].text),"feed_Fecp": str(FecPub_xq(XQuery_feed)[feed_id_XQ].text))}
                       feed_list_XQ.append(feed_XQ)
                 '''
        except Exception as e:
            print(e)





    return feed_list_XQ


# @require_http_methods(["GET"])
def xQuery_filter(request, filter_option, keyword):
    caracol_internacional = 'http://www.caracol.com.co/feed.aspx?id=195'
    caracol_deportes = 'http://www.caracol.com.co/feed.aspx?id=197'
    caracol_entretenimiento = 'http://www.caracol.com.co/feed.aspx?id=201'

    eltiempo_internacional = 'http://www.eltiempo.com/rss/mundo.xml'
    eltiempo_deportes = 'http://www.eltiempo.com/rss/deportes.xml'
    eltiempo_entretenimiento = 'http://www.eltiempo.com/rss/entretenimiento.xml'

    elmundo_internacional = 'http://www.elmundo.com/images/rss/noticias_internacional.xml'
    elmundo_deportes = 'http://www.elmundo.com/images/rss/deportes.xml'
    elmundo_entretenimiento = 'http://www.elmundo.com/images/rss/vida_entretenimiento.xml'

    url_list = []
    url_list.append(caracol_internacional)
    url_list.append(caracol_deportes)
    url_list.append(caracol_entretenimiento)
    url_list.append(eltiempo_internacional)
    url_list.append(eltiempo_deportes)
    url_list.append(eltiempo_entretenimiento)
    url_list.append(elmundo_internacional)
    url_list.append(elmundo_deportes)
    url_list.append(elmundo_entretenimiento)

    response_data = {}
    #    key = request.GET['key']
    response_data["data"] = xQuery_data(url_list, filter_option, keyword)


    return JsonResponse(response_data)




# Para tabla usando regex

def parse_data_regex(feed_url, filter_option, key):

    feed_list = []
    feed_id = 0

    for url in feed_url:
        parsed_feed = feedparser.parse(url)
        print(url)
        for entry in parsed_feed.entries:
            feed_title = entry.title
            regex = ".*" + key + ".*"
            if filter_option == 'title' and re.match(regex, entry.title):
                feed_id += 1
                feed = {"feed_id": feed_id, "feed_title": str(feed_title)}
                feed_list.append(feed)
            elif filter_option == 'description' and re.match(regex, entry.summary):
                feed_id += 1
                feed = {"feed_id": feed_id, "feed_title": str(feed_title)}
                feed_list.append(feed)
            '''
            elif filter_option == 'category' and re.match(regex, entry.category):
                feed_id += 1
                feed = {"feed_id": feed_id, "feed_title": str(feed_title)}
                feed_list.append(feed)
            '''
    return feed_list

def regex_filter(request, filter_option, keyword):
    caracol_internacional = "http://www.caracol.com.co/feed.aspx?id=195"
    caracol_deportes = "http://www.caracol.com.co/feed.aspx?id=197"
    caracol_entretenimiento = "http://www.caracol.com.co/feed.aspx?id=201"

    eltiempo_internacional = "http://www.eltiempo.com/rss/mundo.xml"
    eltiempo_deportes = "http://www.eltiempo.com/rss/deportes.xml"
    eltiempo_entretenimiento = "http://www.eltiempo.com/rss/entretenimiento.xml"

    elmundo_internacional = "http://www.elmundo.com/images/rss/noticias_internacional.xml"
    elmundo_deportes = "http://www.elmundo.com/images/rss/deportes.xml"
    elmundo_entretenimiento = "http://www.elmundo.com/images/rss/vida_entretenimiento.xml"

    url_list = []
    url_list.append(caracol_internacional)
    url_list.append(caracol_deportes)
    url_list.append(caracol_entretenimiento)
    url_list.append(eltiempo_internacional)
    url_list.append(eltiempo_deportes)
    url_list.append(eltiempo_entretenimiento)
    url_list.append(elmundo_internacional)
    url_list.append(elmundo_deportes)
    url_list.append(elmundo_entretenimiento)

    response_data = {}
#    key = request.GET['key']
    response_data["data"] = parse_data_regex(url_list, filter_option, keyword)

    return JsonResponse(response_data)



# Para tabla sin filtrar
def parse_data(feed_url):

    feed_list = []
    feed_id = 0

    for url in feed_url:
        parsed_feed = feedparser.parse(url)
        print(url)
        for entry in parsed_feed.entries:
            feed_id += 1
            feed_title = entry.title
            feed = {"feed_id": feed_id, "feed_title": str(feed_title)}
            feed_list.append(feed)
    return feed_list


def feed_list(request):

    caracol_internacional = "http://www.caracol.com.co/feed.aspx?id=195"
    caracol_deportes = "http://www.caracol.com.co/feed.aspx?id=197"
    caracol_entretenimiento = "http://www.caracol.com.co/feed.aspx?id=201"

    eltiempo_internacional = "http://www.eltiempo.com/rss/mundo.xml"
    eltiempo_deportes = "http://www.eltiempo.com/rss/deportes.xml"
    eltiempo_entretenimiento = "http://www.eltiempo.com/rss/entretenimiento.xml"

    elmundo_internacional = "http://www.elmundo.com/images/rss/noticias_internacional.xml"
    elmundo_deportes = "http://www.elmundo.com/images/rss/deportes.xml"
    elmundo_entretenimiento = "http://www.elmundo.com/images/rss/vida_entretenimiento.xml"

    url_list = []
    url_list.append(caracol_internacional)
    url_list.append(caracol_deportes)
    url_list.append(caracol_entretenimiento)
    url_list.append(eltiempo_internacional)
    url_list.append(eltiempo_deportes)
    url_list.append(eltiempo_entretenimiento)
    url_list.append(elmundo_internacional)
    url_list.append(elmundo_deportes)
    url_list.append(elmundo_entretenimiento)

    response_data = {}
    response_data["data"] = parse_data(url_list)
    print(response_data)
    return JsonResponse(response_data)


#@require_http_methods(["GET"])


# Para tabla usando filtro xquery


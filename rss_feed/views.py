from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import re

import feedparser
import json


def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'rss_feed/index.html', context)


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

    return JsonResponse(response_data)


#@require_http_methods(["GET"])
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
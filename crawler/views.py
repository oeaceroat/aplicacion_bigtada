import json

from django.http import JsonResponse
from django.shortcuts import render
import os
from django.conf import settings

# Create your views here.

def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}

    return render(request, 'crawler/index.html', context)


def lista_profesores(request):

    data = json.load(open(os.path.join(settings.BASE_DIR, 'profesores.json' )))

    return JsonResponse({'data':data})


def lista_noticias(request):
    data = json.load(open(os.path.join(settings.BASE_DIR, 'noticias.json')))
    return JsonResponse({'data': data})
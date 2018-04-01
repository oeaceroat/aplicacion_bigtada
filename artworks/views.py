import base64
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


def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'artworks/index.html', context)


def search_graph(request, title, person, place, year_ini, year_fin):
    response_data = {}
    #    key = request.GET['key']
    # response_data["data"] = xQuery_data(url_list, filter_option, keyword)

    # execute_job(title, person, place, year_ini, year_fin)

    # leer archivo
    result_file = settings.BASE_DIR + '/muestraideal.txt'
    data_graph = leer_fichero_nodos(result_file)

    # armar grafo
    nodes = data_graph[0]
    edges = data_graph[1]


    #nodes = ['Mona lisa', 'B', 'C', 'D', 'E', 'leonardo Da Vincci', 'Hernest Heminhway', 'This book is broken']

    #edges = [('Mona lisa', 'B'),
    #         ('Mona lisa', 'C'), ('C', 'D'), ('D', 'E'), ('E', 'B'),
    #         ('Mona lisa', 'leonardo Da Vincci'),
    #         ('Hernest Heminhway', 'This book is broken'),
    #         ('This book is broken', 'C')]

    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    print('Nodos: ', graph.number_of_nodes())
    print('Realaciones: ', graph.number_of_edges())

    # plt.figure(figsize=(10, 10))

    nx.draw_networkx(G=graph, node_size=100, font_size=8)
    url_graph = settings.BASE_DIR + '/artworks/static/artworks/grafo_pru.png'
    plt.savefig(url_graph, dpi=100)
    print(url_graph)
    plt.clf()
    # graficar y guardar grafo


    return JsonResponse(response_data)


def get_connection():

    proxy_uri = "http://connect.virtual.uniandes.edu.co:22"
    url = urlparse(proxy_uri)

    http_con = http.client.HTTPConnection(url.hostname, url.port)

    ''''
    headers = {}
    if url.username and url.password:
        auth = '%s:%s' % (url.username, url.password)
        headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(auth)
    '''

    # host = 'bigdata-cluster1-01.virtual.uniandes.edu.co' # Cluster de 20 nodos
    host = 'bigdata-cluster2-01.virtual.uniandes.edu.co' # Cluster de 4 nodos

    user = 'bigdata20181001'
    password = 'd0947747a04e26b1b2d152278128d8d2'
    port = 22

    http_con.set_tunnel(host, port)
    http_con.connect()
    sock = http_con.sock

    ssh = paramiko.SSHClient()  # Iniciamos un cliente SSH
    ssh.load_system_host_keys()  # Agregamos el listado de host conocidos
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Si no encuentra el host, lo agrega automáticamente
    ssh.connect(
        hostname=host,
        username=user,
        password=password,
        port=22,
        sock=sock
    )  # Iniciamos la conexión.

    return ssh


def search(ssh_obj, title, person, place, year_ini, year_fin):

    command = f'(cd /home/bigdata20181001/prueba; ' \
              f'spark-submit script_test.py {title} {person} {place} {year_ini} {year_fin})'

    # command_1 = f'(cd /home/bigdata20181001/prueba; ./shell_test.sh)'
    # command_2 = f'(cd /home/bigdata20181001/prueba; spark-submit script_test.py)'

    stdin, stdout, stderr = ssh_obj.exec_command(command)
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())

    scp = SCPClient(ssh_obj.get_transport())
    print('copiando archivo de respuesta')
    scp.get(remote_path=f'/home/bigdata20181001/prueba/salida.txt')
    print('archivo copiado')


def execute_job(filter_option, keyword):
    print("Iniciamos la conexión")
    ssh_obj = get_connection()
    print("Realizamos búsqueda")
    search(ssh_obj, filter_option, keyword)
    ssh_obj.close()
    print('Finalizado correctamente')


def leer_fichero_nodos(entrada):

    nodos = []  # lista nodos
    aristas = []  # lista aristas

    for linea in open(entrada, 'r'):

        linea = linea.strip()
        origen, destino, tiporigen, tipodestino, fecha = linea.split('|')

        if origen not in nodos:
            nodos.append(origen)

        if destino not in nodos:
            nodos.append(destino)

        aristas.append((origen, destino))

    return nodos, aristas

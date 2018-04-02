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


def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    return render(request, 'artworks/index.html', context)


def search_graph(request, title, person, place, year_ini, year_fin):
    response_data = {}

    # Ejecutar búsqueda
    execute_job(title, person, place, year_ini, year_fin)

    # leer archivo
    result_file = settings.BASE_DIR + '/resultado.txt'

    '''
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

    plt.figure(figsize=(20, 10))
    plt.title('Grafo completo')

    # graficar y guardar grafo principal
    nx.draw_networkx(G=graph, node_size=100, font_size=8)
    url_graph = settings.BASE_DIR + '/artworks/static/artworks/grafo_pru.png'
    plt.savefig(url_graph, dpi=100)
    print(url_graph)
    plt.clf()
    '''

    #grafo 2

    data_graph2 = leer_fichero_muestra(result_file)
    nodes2 = data_graph2[0]
    edges2 = data_graph2[1]

    graph2 = nx.DiGraph()
    graph2.add_nodes_from(nodes2)
    graph2.add_edges_from(edges2)

    print('Nodos: ', graph2.number_of_nodes())
    print('Realaciones: ', graph2.number_of_edges())

    plt.figure(figsize=(20, 10))
    plt.title('Muestra del grafo')

    # graficar y guardar grafo principal
    nx.draw_networkx(G=graph2, node_size=100, font_size=10)
    url_graph2 = settings.BASE_DIR + '/artworks/static/artworks/grafo2_pru.png'
    plt.savefig(url_graph2, dpi=100)
    print(url_graph2)
    plt.clf()




    return JsonResponse(response_data)


def get_connection():

    proxy_uri = 'http://connect.virtual.uniandes.edu.co:22'
    url = urlparse(proxy_uri)

    http_con = http.client.HTTPConnection(url.hostname, url.port)

    ''''
    headers = {}
    if url.username and url.password:
        auth = '%s:%s' % (url.username, url.password)
        headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(auth)
    '''

    host = 'bigdata-cluster1-01.virtual.uniandes.edu.co' # Cluster de 20 nodos
    # host = 'bigdata-cluster2-01.virtual.uniandes.edu.co' # Cluster de 4 nodos

    user = 'bigdata20181001'
    password = 'd0947747a04e26b1b2d152278128d8d2'
    port = 22

    http_con.set_tunnel(host, port)
    http_con.connect()
    sock = http_con.sock

    ssh = paramiko.SSHClient()  # Iniciamos un cliente SSH
    ssh.load_system_host_keys()  # Agregamos el listado de host conocidos
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Si no encuentra el host, lo agrega automáticamente
    try:
        ssh.connect(
            hostname=host,
            username=user,
            password=password,
            port=22,
            sock=sock
        )  # Iniciamos la conexión.
    except Exception as e:
        print(str(e))
    return ssh


def search(ssh_obj, title, person, place, year_ini, year_fin):

    title = "'" + title + "'"
    person = "'" + person + "'"
    place = "'" + place + "'"
    year_ini = "'" + year_ini + "'"
    year_fin = "'" + year_fin + "'"

    print('Parametros = ', title, '   ',  person, '   ',  place, '   ',  year_ini, '   ',  year_fin)

    remove_file = '(cd /home/bigdata20181001; rm -R resultado.txt)'
    command = f'(cd /home/bigdata20181001; ' \
              f'spark-submit grafo.py {title} {person} {place} {year_ini} {year_fin})'

    # command_1 = f'(cd /home/bigdata20181001/prueba; ./shell_test.sh)'
    # command_2 = f'(cd /home/bigdata20181001/prueba; spark-submit script_test.py)'

    # Eliminar archvio de resultados en la MEC
    print('Borrando archivo de resultados en la MEC')
    stdin, stdout, stderr = ssh_obj.exec_command(remove_file)
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())

    # Ejecutar búsqueda en el cluster
    print('Éjecutando script en el cluster')
    stdin, stdout, stderr = ssh_obj.exec_command(command)
    print("stderr: ", stderr.readlines())
    print("pwd: ", stdout.readlines())

    # Traer el el archivo de resultados
    scp = SCPClient(ssh_obj.get_transport())
    print('copiando archivo de respuesta')
    scp.get(remote_path=f'/home/bigdata20181001/resultado.txt')
    print('archivo copiado')
    ssh_obj.close()

def execute_job(title, person, place, year_ini, year_fin):
    print("Iniciamos la conexión")
    ssh_obj = get_connection()
    print("Realizamos búsqueda")
    search(ssh_obj,  title, person, place, year_ini, year_fin)

    print('Finalizado correctamente')


def leer_fichero_nodos(entrada):

    nodos = []  # lista nodos
    aristas = []  # lista aristas

    for linea in open(entrada, 'r'):

        linea = linea.strip()
        try:
            origen, destino, tiporigen, tipodestino, fecha, fecha2, nivel = linea.split('|')
        except:
            origen, destino, tiporigen, tipodestino, fecha, fecha2, nivel = linea.split('|')


        if origen not in nodos:
            nodos.append(origen)

        if destino not in nodos and destino:
            nodos.append(destino)

        aristas.append((origen, destino))

    return nodos, aristas


def leer_fichero_muestra(entrada):

    aristas_nivel1 = []
    aristas_nivel2 = []
    nodos = []
    for linea in open(entrada, 'r'):
        linea = linea.strip()
        try:
            origen, destino, tiporigen, tipodestino, fecha, fecha2, nivel = linea.split('|')
        except:
            origen, destino, tiporigen, tipodestino, fecha, fecha2, nivel = linea.split('|')

        if len(aristas_nivel1)<20 and nivel=='1':

            aristas_nivel1.append((origen, destino))
            if origen not in nodos:
                nodos.append(origen)
            if destino not in nodos:
                nodos.append(destino)

        elif len(aristas_nivel2)<20 and nivel=='2':

            aristas_nivel2.append((origen,destino))
            if origen not in nodos:
                nodos.append(origen)
            if destino not in nodos:
                nodos.append(destino)

        if len(aristas_nivel1)==20 and len(aristas_nivel2)==20:
            break

    aristas = aristas_nivel1+aristas_nivel2  # lista aristas
    print ('total aristas ', len(aristas))
    print('total nodos ', len(nodos) )

    return nodos, aristas

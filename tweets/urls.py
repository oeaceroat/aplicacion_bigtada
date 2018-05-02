from django.urls import path

from . import views


app_name = 'tweets'
urlpatterns = [
    path('', views.index, name='index'),
    path('polaridad/', views.getPolaridad, name='polaridad'),
    #path('<str:title>/<str:person>/<str:place>/<str:year_ini>/<str:year_fin>/search_graph/',
     #    views.search_graph, name='search_graph'),
]

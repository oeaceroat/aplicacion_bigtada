from django.urls import path

from . import views


app_name = 'dbpedia'
urlpatterns = [
    path('', views.index, name='index'),
    path('run_enrich/', views.runEnrich, name='runEnrich'),
    path('get_artists/', views.getMusicalArtists, name='get_artists'),
    path('get_songs/', views.getSongs, name='get_songs'),
    path('get_places/', views.getPlaces, name='get_places'),
    path('get_quiestions/', views.getQuestions, name='get_quiestions'),


]

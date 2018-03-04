from django.urls import path

from . import views


app_name = 'crawler'
urlpatterns = [
    path('', views.index, name='index'),
    path('lista_profesores/', views.lista_profesores, name='lista_profesores'),
    path('lista_noticias/', views.lista_noticias, name='lista_noticias'),
    #path('<str:filter_option>/<str:keyword>/regex_filter/', views.regex_filter, name='regex_filter'),
    #path('<str:filter_option>/<str:keyword>/xq_filter/', views.xQuery_filter, name='xq_filter')
]
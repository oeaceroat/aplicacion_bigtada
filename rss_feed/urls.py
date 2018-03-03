from django.urls import path

from . import views


app_name = 'rss_feed'
urlpatterns = [
    path('', views.index, name='index'),
    path('feed_list/', views.feed_list, name='feed_list'),
    path('<str:filter_option>/<str:keyword>/regex_filter/', views.regex_filter, name='regex_filter'),
]

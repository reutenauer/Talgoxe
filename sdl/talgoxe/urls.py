# encoding: UTF-8

from django.conf.urls import url

from . import views

stickord_regexp = ur'^stickord/(?P<stickord>[.M?, TSOHF2a-zåäö()-]+)'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url('create', views.create, name = 'create'),
    url(ur'^(?P<id>\d+)$', views.artikel, name = 'artikel'),
    url(stickord_regexp, views.artikel_efter_stickord, name = 'stickord'),
    url(stickord_regexp + ur'/print', views.print_stickord, name = 'print_stickord'),
    url(r'^print$', views.print_lexicon, name = 'printing'),
]

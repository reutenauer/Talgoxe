# encoding: UTF-8

from django.conf.urls import url

from . import views

stickord_regexp = r'^stickord/(?P<stickord>[0-9.M?, TSOHF2a-zåäö()-]+)'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url('create', views.create, name = 'create'),
    url(r'^(?P<id>\d+)$', views.artikel, name = 'artikel'),
    url(stickord_regexp, views.artikel_efter_stickord, name = 'stickord'),
    url(r'^artiklar/(?P<id>\d+)$', views.artiklar, name = 'artiklar'),
    url(r'^(?P<id>\d+)/print', views.print_artikel, name = 'print_artikel'),
    url(r'^(?P<id>\d+)/odf', views.export_to_odf, name = 'export_to_odf'),
    url(r'^print$', views.print_lexicon, name = 'printing'),
    url(r'^search$', views.search, name = 'search'),
    url(r'^artikel/(?P<id>\d+)(\.(?P<format>\w+))?$', views.article, name = 'article'),
    url(r'print-on-demand', views.print_on_demand, name = 'print_on_demand'),
]

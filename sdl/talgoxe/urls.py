# encoding: UTF-8

from django.conf.urls import url

from . import views

stickord_regexp = ur'^stickord/(?P<stickord>[.M?, TSOHF2a-zåäö()-]+)'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(stickord_regexp + ur'$', views.stickord, name = 'stickord'),
    url(stickord_regexp + ur'/print', views.print_stickord, name = 'print_stickord'),
    url(stickord_regexp + ur'/update$', views.update_stickord, name = 'update_stickord'),
    url(r'^print$', views.print_lexicon, name = 'printing'),
]

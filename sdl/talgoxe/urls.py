# encoding: UTF-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(ur'^stickord/(?P<stickord>[a-zåäö]+)', views.stickord, name = 'stickord'),
]

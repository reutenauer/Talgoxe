# encoding: UTF-8

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url('create', views.create, name = 'create'),
    url(r'^redigera/(?P<id>\d+)$', views.redigera, name = 'redigera'),
    url(r'^stickord/(?P<stickord>.+)$', views.artikel_efter_stickord, name = 'stickord'),
    url(r'^search$', views.search, name = 'search'),
    url(r'^artikel/(?P<id>\d+)?$', views.artikel, name = 'artikel'),
    url(r'print-on-demand$', views.print_on_demand, name = 'print_on_demand'),
    url(r'print-on-demand/pdf', views.print_pdf, name = 'print_pdf'),
    url(r'print-on-demand/odf', views.print_odf, name = 'print_odf'),
    url(r'print-on-demand/docx', views.print_docx, name = 'print_docx'),
    url(r'logout', views.easylogout, name = 'easylogout'),
]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp
from os import system, chdir
import io
import os
import re

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader, Context

from talgoxe.models import Lemma, Lexicon
from django import VERSION

def index(request):
    return common(request, 'dagom')

def stickord(request, stickord):
    return common(request, stickord)

def update_stickord(request, stickord):
    template = loader.get_template('talgoxe/update-word.html')
    keys = []
    for key in request.POST.keys():
        match = re.match(ur'type-(\d+)', key)
        if match:
            id = int(match.group(1))
            keys.append(id)

    context = {
        'keys' : keys
    }

    return HttpResponse(template.render(context, request))

def print_stuff(request, stickord = None):
    return HttpResponse('<p>Please do not press this button again.</p>')

    tempdir = mkdtemp('', 'SDLartikel')
    sourcename = tempdir + '/sdl.tex'
    source = open(sourcename, 'w')
    source.write("\\setupbodyfont[pagella, 12pt]\n")
    if stickord:
        source.write("\\setuppagenumbering[state=stop]\n")
    with io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'sdl-setup.tex')) as file:
        source.write(file.read().encode('UTF-8'))

    source.write("""
        \\starttext
        """.encode('UTF-8'))

    if stickord:
        lemma = Lemma.objects.filter(lemma = stickord).first()
        source.write("\\startcolumns[n=2,balance=no]\n")
        lemma.process(source)
        source.write("\\stopcolumns\n")
    else:
        source.write("\\startcolumns[n=2,balance=yes]\n")
        for lemma in Lemma.objects.filter(id__gt = 0).order_by('lemma'):
            source.write("\\startparagraph\n")
            lemma.process(source)
            source.write("\\stopparagraph\n")
        source.write("\\stopcolumns")

    source.write("\\stoptext\n")
    source.close()
    chdir(tempdir)
    system("context --batchmode sdl.tex")
    if stickord:
        basename = lemma.lemma
    else:
        basename = 'sdl'
    ordpdfpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'ord', '%s.pdf' % basename)
    print("Copying sdl.pdf to %s" % ordpdfpath)
    system(("cp sdl.pdf %s" % ordpdfpath).encode('UTF-8'))
    return HttpResponse("<p><a href='/static/ord/%s.pdf'>Click here</a></p>" % lemma.lemma)

def print_stickord(request, stickord):
    return print_stuff(request, stickord)

def print_lexicon(request):
    return print_stuff(request)

def common(request, stickord):
    template = loader.get_template('talgoxe/index.html')
    lemmata = Lemma.objects.filter(id__gt = 0).order_by('lemma')
    lemma = Lemma.objects.filter(lemma = stickord).first()
    print stickord
    print lemma.lemma
    lemma.resolve_pilcrow()
    lemma.collect()
    context = {
        'input': lemma.raw_data_set(),
        'segments': lemma.segments,
        'lemma': lemma,
        'lemmata': lemmata,
        'new_segments': lemma.new_segments
    }

    if VERSION[1] == 7:
        return HttpResponse(template.render(Context(context))) # Django 1.7
    else:
        return HttpResponse(template.render(context, request)) # Django 1.11

def printing(request):
    lexicon = Lexicon()
    lexicon.process()
    return HttpResponse('<p>Preparing to print!</p>');

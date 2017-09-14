# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp
from os import system, chdir
import io
import os

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from talgoxe.models import Lemma, Lexicon

def index(request):
    return common(request, 'dagom')

def stickord(request, stickord):
    return common(request, stickord)

def doprint(request, stickord):

def print_stuff(request, stickord = None):
    tempdir = mkdtemp('', 'SDLartikel')
    sourcename = tempdir + '/sdl.tex'
    source = open(sourcename, 'w')
    source.write("""
        \\setupbodyfont[pagella, 12pt]
        \\setuppagenumbering[state=stop]

        """)
    with io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'sdl-setup.tex')) as file:
        source.write(file.read().encode('UTF-8'))

    source.write("""
        \\starttext
        """.encode('UTF-8'))

    if stickord:
        lemma = Lemma.objects.filter(lemma = stickord).first()
        lemma.process(source)
    else:
        for lemma in Lemma.objects.filter(id__gt = 0).order_by('lemma'):
              lemma.process(source)

    source.write("\\stoptext\n")
    source.close()
    chdir(tempdir)
    system("context sdl.tex")
    return HttpResponse("<p><a href='file://%s'>Click here</a></p>" % sourcename.replace(r'.tex', '.pdf'))

def print_stickord(request, stickord):

def print_lexicon(request):

def common(request, stickord):
    template = loader.get_template('talgoxe/index.html')
    lemmata = Lemma.objects.filter(id__gt = 0).order_by('lemma')
    lemma = Lemma.objects.filter(lemma = stickord).first()
    print stickord
    print lemma.lemma
    lemma.resolve_pilcrow()
    context = {
        'input': lemma.raw_data_set(),
        'segments': lemma.segments,
        'lemma': lemma,
        'lemmata': lemmata
    }

    return HttpResponse(template.render(context, request))

def printing(request):
    lexicon = Lexicon()
    lexicon.process()
    return HttpResponse('<p>Preparing to print!</p>');

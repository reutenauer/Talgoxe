# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp
from os import system, chdir

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from talgoxe.models import Lemma, Lexicon

def index(request):
    return common(request, 'dagom')

def stickord(request, stickord):
    return common(request, stickord)

def print_stickord(request, stickord):
    lemma = Lemma.objects.filter(lemma = stickord).first()
    tempdir = mkdtemp('', 'SDLartikel')
    sourcename = tempdir + '/sdl-artikel.tex'
    source = open(sourcename, 'w')
    source.write("""
        \\setupbodyfont[pagella, 12pt]
        \\setuppagenumbering[state=stop]

        \\starttext
        """)
    lemma.process(source)
    source.write("\\stoptext\n")
    source.close()
    chdir(tempdir)
    system("context sdl-artikel.tex")
    return HttpResponse("<p><a href='file://%s</a></p>" % sourcename.replace(r'.tex', '.pdf'))

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

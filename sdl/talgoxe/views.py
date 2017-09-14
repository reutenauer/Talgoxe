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

        \\catcode`\\:=11
        \\catcode`\\Ö=11
        \\def\\SDL:SO#1{{\\bf #1}}
        \\def\\SDL:OK#1{{\\bfx #1}}
        \\def\\SDL:KO#1{}
        \\def\\SDL:G#1{{\\tfx #1}}
        \\def\\SDL:DSP#1{{\\it #1}}
        \\def\\SDL:SP#1{{\\it #1}}
        \\def\\SDL:TIP#1{{\\tfx #1}}
        \\def\\SDL:IP#1{{\\kern-0.3em #1}}
        \\def\\SDL:M#1#2{{\\bf #2}}
        \\def\\SDL:M#1#2{{\\bf #2}}
        \\def\\SDL:VH#1{{#1\\kern-0.3em}}
        \\def\SDL:HH#1{{\\kern-0.3em #1}}
        \\def\\SDL:VR#1{{#1\\kern-0.3em}}
        \\def\\SDL:HR#1{{\\kern-0.3em #1}}
        \\def\\SDL:REF#1{{\\bfx #1}}
        \\def\SDL:FO#1{{\\it #1}}
        \\def\\SDL:TIK#1{{\\tfx\\it #1}}
        \\def\\SDL:FLV#1{{\\bfx #1}}
        \\def\\SDL:ÖVP#1{{(#1)}}
        \\def\\SDL:BE#1{#1}
        \\def\SDL:ÖV#1{#1}

        \\starttext
        """.encode('UTF-8'))
    lemma.process(source)
    source.write("\\stoptext\n")
    source.close()
    chdir(tempdir)
    system("context sdl-artikel.tex")
    # return HttpResponse("ConTeXt has run!")
    # return HttpResponse(sourcename)
    return HttpResponse("<p><a href='file://%s'>Click here</a></p>" % sourcename.replace(r'.tex', '.pdf'))
    # return HttpResponse("<p><a href='file://%s</a></p>" % sourcename.replace(r'.tex', '.pdf'))

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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from talgoxe.models import Lemma

def index(request):
    return common(request, 'dagom')

def stickord(request, stickord):
    return common(request, stickord)

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

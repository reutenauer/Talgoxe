# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from talgoxe.models import Lemma

def index(request):
    template = loader.get_template('talgoxe/index.html')
    lemmata = Lemma.objects.order_by('lemma')[:31]
    # lemma = lemmata.first()
    lemma = Lemma.objects.get(lemma = 'dagom')
    context = {
        # 'data': [1, 2, 3],
        'data': lemma.data_set.filter(id__gt = 0).order_by('pos'),
        'lemma': lemma,
        'lemmata': lemmata
    }
    return HttpResponse(template.render(context, request))

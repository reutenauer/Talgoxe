# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp, mktemp
import logging
from os import system, chdir, popen, rename, environ
from os.path import join, dirname, abspath
import io
import re
from collections import OrderedDict, deque
from docx import Document

from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings

from django.shortcuts import render, redirect

# Create your views here.

from django import VERSION
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
if VERSION[1] == 7 or VERSION[1] == 8:
    from django.core.urlresolvers import reverse
    from django.template import RequestContext
    from django.views.decorators.csrf import csrf_protect
else:
    from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.contrib.auth import logout

from talgoxe.models import Spole, Artikel, Typ, Exporter, UnsupportedFormat

def render_template(request, template, context):
    if VERSION[1] == 7:
        return HttpResponse(template.render(RequestContext(request, context))) # Django version 1.7
    else:
        return HttpResponse(template.render(context, request)) # Django version 1.11

@login_required
def index(request):
    template = loader.get_template('talgoxe/index.html')
    lemmata = Artikel.objects.order_by('lemma', 'rang')
    context = { 'lemmata' : lemmata, 'pagetitle' : "Talgoxe – Svenskt dialektlexikon", 'checkboxes' : False }
    return render_template(request, template, context)

@login_required # FIXME Något om användaren faktiskt är utloggad?
def create(request):
    stickord = request.POST['ny_stickord'].strip()
    företrädare = Artikel.objects.filter(lemma = stickord)
    maxrang = företrädare.aggregate(Max('rang'))['rang__max']
    if maxrang == None:
        rang = 0
    elif maxrang == 0:
        lemma0 = företrädare.first()
        lemma0.rang = 1
        lemma0.save()
        rang = 2
    elif maxrang > 0:
        rang = maxrang + 1
    lemma = Artikel.objects.create(lemma = stickord, rang = rang)
    return HttpResponseRedirect(reverse('redigera', args = (lemma.id,)))

@login_required
def redigera(request, id):
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        artikel = Artikel.objects.get(id = id)
        artikel.update(request.POST)

    template = loader.get_template('talgoxe/redigera.html')
    artiklar = Artikel.objects.order_by('lemma', 'rang') # Anm. Svensk alfabetisk ordning verkar funka på frigg-test! Locale?
    artikel = Artikel.objects.get(id = id)
    artikel.collect()
    context = {
        'lemma': artikel,
        'lemmata': artiklar,
        'pagetitle': "%s – redigera i Svenskt dialektlexikon" % artikel.lemma,
    }

    return render_template(request, template, context)

@login_required
def artikel_efter_stickord(request, stickord):
    lemmata = Artikel.objects.filter(id__gt = 0, lemma = stickord).order_by('rang')
    # TODO: 0!
    if len(lemmata) == 1:
        return HttpResponseRedirect(reverse('redigera', args = (lemmata.first().id,)))
    else:
        template = loader.get_template('talgoxe/stickord.html')
        context = {
            'lemmata' : lemmata
        }
        return render_template(request, template, context)

def export_to_pdf(request, ids):
    tempdir = mkdtemp('', 'SDLartikel')
    sourcename = join(tempdir, 'sdl.tex')
    import locale
    locale.setlocale(locale.LC_CTYPE, 'sv_SE.UTF-8')
    loc = locale.getpreferredencoding('False')
    source = open(sourcename, 'w')
    source.write("\\mainlanguage[sv]")
    source.write("\\setupbodyfont[pagella, 12pt]\n")
    source.write("\\setuppagenumbering[state=stop]\n")
    with io.open(join(dirname(abspath(__file__)), 'lib', 'sdl-setup.tex'), 'r', encoding = 'UTF-8') as file:
        source.write(file.read())

    source.write("""
        \\starttext
        """)

    ids = sorted(ids, key = lambda id: Artikel.objects.get(id = id).lemma)
    source.write("\\startcolumns[n=2,balance=yes]\n")
    for id in ids:
        lemma = Artikel.objects.get(id = id)
        lemma.process(source)
        source.write("\\par")
    if len(ids) == 1:
        basename = '%s-%s' % (ids[0], Artikel.objects.get(id = ids[0]).lemma)
    else:
        basename = 'sdl-utdrag' # FIXME Needs timestamp osv.
    source.write("\\stopcolumns\n")

    source.write("\\stoptext\n")
    source.close()

    chdir(tempdir)
    environ['PATH'] = "%s:%s" % (settings.CONTEXT_PATH, environ['PATH'])
    environ['TMPDIR'] = '/tmp'
    popen("context --batchmode sdl.tex").read()
    ordpdfpath = join(dirname(abspath(__file__)), 'static', 'ord', '%s.pdf' % basename)
    rename(join(tempdir, 'sdl.pdf'), ordpdfpath)
    template = loader.get_template('talgoxe/download_pdf.html')
    context = { 'filepath' : 'ord/%s.pdf' % basename }
    return render_template(request, template, context)

@login_required
def search(request): # TODO Fixa lista över artiklar när man POSTar efter omordning
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        ordning = []
        for artikel in request.POST:
            if re.match('^artikel-', artikel):
                id = artikel.replace('artikel-', '')
                ordning.append(Artikel.objects.get(id = id))
        föreArtikel = ordning[0]
        föreRang = 1
        for artikel in ordning[1:]:
            if artikel.lemma != föreArtikel.lemma and föreRang == 1:
                föreRang = 0
            if föreArtikel.rang != föreRang:
                föreArtikel.rang = föreRang
                föreArtikel.save()
            if artikel.lemma == föreArtikel.lemma:
                föreRang += 1
            else:
                föreRang = 1
            föreArtikel = artikel
    template = loader.get_template('talgoxe/search.html')
    uri = "%s://%s%s" % (request.scheme, request.META['HTTP_HOST'], request.path)
    if 'q' in request.GET:
        söksträng = request.GET['q']
    else:
        return render_template(request, template, { 'q' : 'NULL', 'uri' : uri })
    if 'sök-överallt' in request.GET and request.GET['sök-överallt'] != 'None':
        sök_överallt = request.GET['sök-överallt']
    else:
        sök_överallt = None
    if sök_överallt:
        sök_överallt_eller_inte = 'söker överallt'
    else:
        sök_överallt_eller_inte = 'söker bara uppslagsord'
    lemmata = list(Artikel.objects.filter(lemma__contains = söksträng))
    if sök_överallt:
        spolar = Spole.objects.filter(text__contains = söksträng).select_related('artikel')
        lemmata += [spole.artikel for spole in spolar]
    lemmata = sorted(list(OrderedDict.fromkeys(lemmata)), key = lambda lemma: (lemma.lemma, lemma.rang))
    context = {
            'q' : söksträng,
            'lemmata' : lemmata,
            'titel' : '%d sökresultat för ”%s” (%s)' % (len(lemmata), söksträng, sök_överallt_eller_inte),
            'uri' : uri,
            'sök_överallt' : sök_överallt,
        }

    return render_template(request, template, context)

@login_required
def artikel(request, id):
    artikel = Artikel.objects.get(id = id)
    template = loader.get_template('talgoxe/artikel.html')
    artikel.collect()
    context = { 'lemma' : artikel, 'format' : format }

    return render_template(request, template, context)

@login_required
def print_on_demand(request):
    method = request.META['REQUEST_METHOD']
    template = loader.get_template('talgoxe/print_on_demand.html')
    if method == 'POST':
        lemmata = []
        for key in request.POST:
            mdata = re.match('selected-(\d+)', key)
            bdata = re.match('bokstav-(.)', key)
            if mdata:
                lemma = Artikel.objects.get(id = int(mdata.group(1)))
                # lemma.collect()
                lemmata.append(lemma)
            elif bdata:
                hel_bokstav = Artikel.objects.filter(lemma__startswith = bdata.group(1))
                # deque(map(lambda lemma: lemma.collect(), hel_bokstav), maxlen = 0)
                lemmata += hel_bokstav
        lemmata = sorted(lemmata, key = lambda lemma: (lemma.lemma, lemma.rang)) # TODO Make unique
        context = { 'lemmata' : lemmata, 'redo' : True, 'titel' : 'Ditt urval på %d artiklar' % len(lemmata) }
        template = loader.get_template('talgoxe/search.html')
    elif method == 'GET':
        lemmata = Artikel.objects.order_by('lemma', 'rang')
        bokstäver = [chr(i) for i in range(0x61, 0x7B)] + ['å', 'ä', 'ö']
        context = { 'lemmata' : lemmata, 'checkboxes' : True, 'bokstäver' : bokstäver }

    return render_template(request, template, context)

@login_required
def print_pdf(request):
    return export_to_pdf(request, list(map(lambda s: s.strip(), request.GET['ids'].split(','))))

@login_required
def print(request, format):
    if format not in ['odf', 'docx']:
        raise UnsupportedFormat(format)
    template = loader.get_template('talgoxe/download_document.html')
    exporter = Exporter(format)
    filepath = exporter.export(list(map(lambda s: s.strip(), request.GET['ids'].split(','))))
    context = { 'filepath' : filepath }

    return render_template(request, template, context)

def easylogout(request):
    logout(request)
    template = loader.get_template("talgoxe/logout.html")
    return render_template(request, template, { })

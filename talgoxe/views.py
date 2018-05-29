# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp, mktemp
from os import system, chdir
import io
import os
from os.path import join
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

from talgoxe.models import Spole, Artikel, Lexicon, Typ

def render_template(request, template, context):
    if VERSION[1] == 7:
        return HttpResponse(template.render(RequestContext(request, context))) # Django version 1.7
    else:
        return HttpResponse(template.render(context, request)) # Django version 1.11

@login_required
def index(request):
    template = loader.get_template('talgoxe/index.html')
    lemmata = Artikel.objects.filter(id__gt = 0).order_by('lemma', 'rang')
    context = { 'lemmata' : lemmata, 'pagetitle' : "Talgoxe – Svenskt dialektlexikon", 'checkboxes' : False }
    return render_template(request, template, context)

@login_required # FIXME Något om användaren faktiskt är utloggad?
def create(request):
    stickord = request.POST['ny_stickord'].strip()
    print("Fick lemma ’%s’" % stickord)
    företrädare = Artikel.objects.filter(lemma = stickord)
    maxrank = företrädare.aggregate(Max('rang'))['rang__max']
    if maxrank == None:
        rank = 0
    elif maxrank == 0:
        print("==== 0 = Hej, numrerar om ett lemma...")
        lemma0 = företrädare.first()
        lemma0.rang = 1
        lemma0.save()
        rank = 2
    elif maxrank > 0:
        print("==== 1+")
        rank = maxrank + 1
    else:
        print("==== None")
    lemma = Artikel.objects.create(lemma = stickord, rang = rank)
    return HttpResponseRedirect(reverse('artikel', args = (lemma.id,)))

@login_required
def artikel(request, id):
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        print(request.POST)
        lemma = Artikel.objects.get(id = id)
        lemma.update(request.POST)

    template = loader.get_template('talgoxe/redigera.html')
    lemmata = Artikel.objects.filter(id__gt = 0).order_by('lemma','rang') # Anm. Svensk alfabetisk ordning verkar funka på frigg-test! Locale?
    lemma = Artikel.objects.filter(id = id).first()
    print(id)
    print(lemma.lemma)
    # lemma.resolve_pilcrow()
    lemma.collect()
    if len(lemma.raw_data_set()) == 0:
        ok = Typ.objects.get(kod = 'OK')
        d = Spole(typ_id = ok.id, text = '', pos = 0)
        input = [d]
    else:
        input = lemma.raw_data_set()
    context = {
        'input': input,
        'segments': lemma.segments,
        'lemma': lemma,
        'lemmata': lemmata,
        'new_segments': lemma.new_segments,
        'pagetitle': "%s – redigera i Svenskt dialektlexikon" % lemma.lemma,
    }

    return render_template(request, template, context)

@login_required
def artiklar(request, id):
    template = loader.get_template('talgoxe/artiklar.html')
    lemmata = Artikel.objects.order_by('lemma')
    lemma = Artikel.objects.get(id = id)
    count = lemmata.filter(lemma__lt = lemma.lemma).count()
    simple_lemmata = lemmata.all()[count:count + 10]
    extracted_lemmata = []
    for simple_lemma in simple_lemmata:
        simple_lemma.collect()
        extracted_lemmata += [simple_lemma]
    context = {
        'lemma': lemma,
        'lemmata': lemmata,
        'rank': count,
        'extracted_lemmata': extracted_lemmata,
        'pagetitle': "%s följ. – Svenskt dialektlexikon" % lemma.lemma,
    }

    return render_template(request, template, context)

@login_required
def artikel_efter_stickord(request, stickord):
    lemmata = Artikel.objects.filter(id__gt = 0, lemma = stickord).order_by('rang')
    # TODO: 0!
    if len(lemmata) == 1:
        return HttpResponseRedirect(reverse('artikel', args = (lemmata.first().id,)))
    else:
        template = loader.get_template('talgoxe/stickord.html')
        context = {
            'lemmata' : lemmata
        }
        return render_template(request, template, context)

def print_stuff(request, id = None):
    print(id)
    tempdir = mkdtemp('', 'SDLartikel')
    sourcename = os.path.join(tempdir, 'sdl.tex')
    import locale
    locale.setlocale(locale.LC_CTYPE, 'sv_SE.UTF-8')
    loc = locale.getpreferredencoding('False')
    source = open(sourcename, 'w')
    source.write("\\mainlanguage[sv]")
    source.write("\\setupbodyfont[pagella, 12pt]\n")
    if id:
        source.write("\\setuppagenumbering[state=stop]\n")
    with io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'sdl-setup.tex'), 'r', encoding = 'UTF-8') as file:
        source.write(file.read())

    source.write("""
        \\starttext
        """)

    if id:
        print(type)
        print(id)
        print(type(id))
        if type(id) == str:
            source.write("\\startcolumns[n=2,balance=no]\n")
            lemma = Artikel.objects.get(id = id)
            lemma.process(source)
            basename = '%s-%s' % (id, lemma.lemma)
        elif type(id) == list:
            id = sorted(id, key = lambda id: Artikel.objects.get(id = id).lemma)
            source.write("\\startcolumns[n=2,balance=yes]\n")
            for i in id:
                lemma = Artikel.objects.get(id = i)
                lemma.process(source)
                source.write("\\par")
            if len(id) == 1:
                basename = '%s-%s' % (id[0], Artikel.objects.get(id = id[0]).lemma)
            else:
                basename = 'sdl-utdrag' # FIXME Needs timestamp osv.
        source.write("\\stopcolumns\n")
    else:
        source.write("\\startcolumns[n=2,balance=yes]\n")
        for lemma in Artikel.objects.filter(id__gt = 0).order_by('lemma'):
            source.write("\\startparagraph\n")
            # source.write("{\\bf %s\\par}" % lemma.lemma)
            lemma.process(source)
            source.write("\\stopparagraph\n")
        source.write("\\stopcolumns")
        basename = 'sdl'

    source.write("\\stoptext\n")
    source.close()
    resourcefile = open(sourcename)
    resource = resourcefile.read()
    resourcefile.close()

    return run_context(request, tempdir,  basename)

def run_context(request, tempdir, basename):
    print(tempdir)
    chdir(tempdir)
    os.environ['PATH'] = "%s:%s" % (settings.CONTEXT_PATH, os.environ['PATH'])
    os.environ['TMPDIR'] = '/tmp'
    path = os.environ['PATH']
    from os import popen
    output = popen("context --batchmode sdl.tex")
    import logging
    logger = logging.getLogger('django')
    logger.log(logging.DEBUG, output.read())
    ordpdfpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'ord', '"%s".pdf' % basename)
    print("Copying sdl.pdf to %s" % ordpdfpath)
    system(("cp sdl.pdf %s" % ordpdfpath).encode('UTF-8'))
    logfile = open(os.path.join(tempdir, 'sdl.log'))
    log = logfile.read()
    logfile.close()
    template = loader.get_template('talgoxe/download_pdf.html')
    context = { 'filepath' : 'ord/%s.pdf' % basename }
    return render_template(request, template, context)

def print_artikel(request, id):
    return print_stuff(request, id)

def print_lexicon(request):
    return print_stuff(request)

def printing(request):
    lexicon = Lexicon()
    lexicon.process()
    return HttpResponse('<p>Preparing to print!</p>');

def export_to_odf(request, id):
    print(type(id))
    print(id)
    tempfilename = mktemp('.odt')
    odf = Artikel.start_odf(tempfilename)
    if type(id) == str:
        lemma = Artikel.objects.get(id = id)
        lemma.process_odf(odf)
        finalname = "%s-%s.odt" % (id, lemma.lemma)
    elif type(id) == list:
        for i in id:
            lemma = Artikel.objects.get(id = i)
            lemma.process_odf(odf)
        finalname = 'sdl-utdrag.odt' # FIXME Unikt namn osv.
        if len(id) == 1:
            finalname = '%s-%s.odt' % (id[0], Artikel.objects.get(id = id[0]).lemma)
    Artikel.stop_odf(odf)
    staticpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'ord')
    os.rename(tempfilename, join(staticpath, finalname))
    # system('mv %s %s/"%s"' % (tempfilename, staticpath, finalname))
    template = loader.get_template('talgoxe/download_odf.html')
    context = { 'filepath' : join('ord', finalname) }
    return render_template(request, template, context)

def export_to_docx(request, ids):
  tempfilename = mktemp('.docx')
  print("ids:")
  print(ids)
  if len(ids) == 1:
      id = ids[0]
      lemma = Artikel.objects.get(id = id)
      print(tempfilename)
      docx = lemma.process_docx(tempfilename)
      filename = '%s-%s.docx' % (id, lemma.lemma)
  else:
      filename = 'sdl-utdrag.docx'
      document = Document()
      Artikel.add_docx_styles(document)
      for i in ids:
          lemma = Artikel.objects.get(id = i)
          lemma.generate_docx_paragraph(document)
      document.save(tempfilename)
  staticpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'ord')
  os.rename(tempfilename, join(staticpath, filename))
  template = loader.get_template('talgoxe/download_odf.html')
  context = {'filepath': join('ord', filename)}

  return render_template(request, template, context)

@login_required
def search(request):
    print(request.GET)
    print(request.path)
    template = loader.get_template('talgoxe/search.html')
    if 'q' in request.GET:
        söksträng = request.GET['q']
        print(söksträng)
    else:
        uri = "%s://%s%s" % (request.scheme, request.META['HTTP_HOST'], request.path)
        return render_template(request, template, { 'q' : 'NULL', 'uri' : uri })
    if 'sök-överallt' in request.GET:
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
    lemmata = sorted(list(OrderedDict.fromkeys(lemmata)), key = lambda lemma: lemma.lemma)
    context = {
            'q' : söksträng,
            'lemmata' : lemmata,
            'titel' : '%d sökresultat för ”%s” (%s)' % (len(lemmata), söksträng, sök_överallt_eller_inte),
        }

    return render_template(request, template, context)

@login_required
def article(request, id):
    lemma = Artikel.objects.get(id = id)
    template = loader.get_template('talgoxe/artikel.html')
    lemma.collect()
    context = { 'lemma' : lemma, 'new_segments' : lemma.new_segments, 'format' : format }

    return render_template(request, template, context)

def partial_article(request, id, format):
    lemma = Artikel.objects.get(id = id)
    if format == 'html':
        return HttpResponseRedirect(reverse('article', args = (id,)))
    elif format == 'tex':
        output = io.StringIO()
        lemma.process(output)
        tex = output.getvalue()
        output.close()

        return HttpResponse(tex)
    elif format == 'odf':
        return HttpResponse(lemma.serialise())

@login_required
def print_on_demand(request):
    method = request.META['REQUEST_METHOD']
    template = loader.get_template('talgoxe/print_on_demand.html')
    if method == 'POST':
        print(request.POST)
        lemmata = []
        print('----')
        for key in request.POST:
            mdata = re.match('selected-(\d+)', key)
            bdata = re.match('bokstav-(.)', key)
            if mdata:
                print(mdata.group(1))
                lemma = Artikel.objects.get(id = int(mdata.group(1)))
                # lemma.collect()
                lemmata.append(lemma)
            elif bdata:
                print(bdata.group(1))
                hel_bokstav = Artikel.objects.filter(lemma__startswith = bdata.group(1))
                # deque(map(lambda lemma: lemma.collect(), hel_bokstav), maxlen = 0)
                lemmata += hel_bokstav
        print('----')
        lemmata = sorted(lemmata, key = lambda lemma: (lemma.lemma, lemma.rang)) # TODO Make unique
        context = { 'lemmata' : lemmata, 'redo' : True, 'titel' : 'Ditt urval på %d artiklar' % len(lemmata) }
        print("Number of lemmata:")
        print(len(lemmata))
        template = loader.get_template('talgoxe/search.html')
    elif method == 'GET':
        lemmata = Artikel.objects.order_by('lemma', 'rang')
        bokstäver = [chr(i) for i in range(0x61, 0x7B)] + ['å', 'ä', 'ö']
        context = { 'lemmata' : lemmata, 'checkboxes' : True, 'bokstäver' : bokstäver }

    return render_template(request, template, context)

@login_required
def print_pdf(request):
    print(request.GET)
    ids = []
    # for id in request.GET:
        # value = map(lambda s: s.strip(), request.GET[id].split(','))
        # ids.append([id, deque(map(lambda s: s.strip(), request.GET[id].split(',')))])
        # value = list(map(lambda s: s.strip(), request.GET[id].split(',')))
        # ids.append([id, value])
    # list(map(lambda s: s.strip(), request.GET['ids'].split(',')))
    retvalue = ""
    tex = io.StringIO()
    return print_stuff(request, list(map(lambda s: s.strip(), request.GET['ids'].split(','))))
    template = loader.get_template("talgoxe/download_custom_pdf.html")
    context = { }
    return render_template(request, template, context)

@login_required
def print_odf(request):
    print(request.GET)
    return export_to_odf(request, list(map(lambda s: s.strip(), request.GET['ids'].split(','))))

@login_required
def print_docx(request):
    return export_to_docx(request, list(map(lambda s: s.strip(), request.GET['ids'].split(','))))

def easylogout(request):
    logout(request)
    template = loader.get_template("talgoxe/logout.html")
    return render_template(request, template, { })

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tempfile import mkdtemp, mktemp
from os import system, chdir
import io
import os
import re
import ezodf
from ezodf import newdoc, Heading, Paragraph
from django.conf import settings

from django.shortcuts import render

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

from talgoxe.models import Data, Lemma, Lexicon, Type

def render_template(request, template, context):
    if VERSION[1] == 7:
        return HttpResponse(template.render(RequestContext(request, context))) # Django version 1.7
    else:
        return HttpResponse(template.render(context, request)) # Django version 1.11

def index(request):
    template = loader.get_template('talgoxe/index.html')
    lemmata = Lemma.objects.filter(id__gt = 0).order_by('lemma')
    context = { 'lemmata' : lemmata }
    return render_template(request, template, context)

def create(request):
    lemma = Lemma.objects.create(lemma = request.POST['ny_stickord'])
    return HttpResponseRedirect(reverse('artikel', args = (lemma.id,)))

def artikel(request, id):
    method = request.META['REQUEST_METHOD']
    if method == 'POST':
        print(request.POST)
        lemma = Lemma.objects.get(id = id)
        lemma.update(request.POST)

    template = loader.get_template('talgoxe/artikel.html')
    lemmata = Lemma.objects.filter(id__gt = 0).order_by('lemma') # Anm. Svensk alfabetisk ordning verkar funka på frigg-test! Locale?
    lemma = Lemma.objects.filter(id = id).first()
    print(id)
    print(lemma.lemma)
    lemma.resolve_pilcrow()
    lemma.collect()
    if len(lemma.raw_data_set()) == 0:
        ok = Type.objects.get(abbrev = 'OK')
        d = Data(type_id = ok.id, d = '', pos = 0)
        input = [d]
    else:
        input = lemma.raw_data_set()
    context = {
        'input': input,
        'segments': lemma.segments,
        'lemma': lemma,
        'lemmata': lemmata,
        'new_segments': lemma.new_segments
    }

    return render_template(request, template, context)

def artikel_efter_stickord(request, stickord):
    lemmata = Lemma.objects.filter(id__gt = 0, lemma = stickord)
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
    if id:
        lemma = Lemma.objects.get(id = id)
    tempdir = mkdtemp('', 'SDLartikel')
    sourcename = tempdir + '/sdl.tex'
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
    resourcefile = open(sourcename)
    resource = resourcefile.read()
    resourcefile.close()
    chdir(tempdir)
    os.environ['PATH'] = "%s:%s" % (settings.CONTEXT_PATH, os.environ['PATH'])
    os.environ['TMPDIR'] = '/tmp'
    path = os.environ['PATH']
    from os import popen
    output = popen("context --batchmode sdl.tex")
    import logging
    logger = logging.getLogger('django')
    logger.log(logging.DEBUG, output.read())
    if id:
        basename = str(id) + '-' + lemma.lemma
    else:
        basename = 'sdl'
    ordpdfpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'ord', '"%s".pdf' % basename)
    print("Copying sdl.pdf to %s" % ordpdfpath)
    system(("cp sdl.pdf %s" % ordpdfpath).encode('UTF-8'))
    logfile = open(sourcename.replace('.tex', '.log'))
    log = logfile.read()
    logfile.close()
    template = loader.get_template('talgoxe/download_pdf.html')
    context = { 'filepath' : 'ord/%s-%s.pdf' % (id, lemma.lemma) }
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
    lemma = Lemma.objects.get(id = id)
    tempfilename = mktemp('.odt')
    odt = ezodf.newdoc(doctype = 'odt', filename = tempfilename)
    odt.inject_style('<style:style style:name="SO" style:family="text"><style:text-properties fo:font-weight="bold" /></style:style>')
    odt.body += Heading(lemma.lemma)
    lemma.resolve_pilcrow()
    lemma.collect()
    for segment in lemma.new_segments:
        if segment.type.__str__() == 'SO':
            odt.body += Paragraph(' ' + segment.format(), style_name = 'SO')
        else:
            odt.body += Paragraph(' ' + segment.format())
    odt.save()
    finalname = "%s-%s.odt" % (id, lemma.lemma)
    staticpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'ord')
    system('mv %s %s/"%s"' % (tempfilename, staticpath, finalname))
    template = loader.get_template('talgoxe/download_odf.html')
    context = { 'filepath' : 'ord/%s-%s.odt' % (id, lemma.lemma) }
    return render_template(request, template, context)

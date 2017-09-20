# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from tempfile import mkdtemp

from django.db import models

# Create your models here.

# Not using migration; instead dump the SQL, remove the AUTO_INCREMENT FROM primary keys,
# and copy the existing table into them.  For Data (table fdata), this is needed:
# INSERT INTO talgoxe_data (id, d, pos, lemma_id, type_id) SELECT d_id, d, pos, l_id, typ FROM fdata WHERE typ IN (SELECT nr FROM typer) AND l_id IN (SELECT l_id FROM lemma);
# Foreign keys fails otherwise!
class Lemma(models.Model):
    lemma = models.CharField(max_length = 100)
    segments = []

    def __str__(self):
        return self.lemma

    def __unicode__(self):
        return self.lemma

    def raw_data_set(self):
        return self.data_set.filter(id__gt = 0).order_by('pos')

    def resolve_pilcrow(self):
        i = 0
        currmoment1 = []
        currmoment2 = []
        self.segments = []
        state = 'INITIAL'
        gtype = None
        while i < self.raw_data_set().count():
            currseg = self.raw_data_set().all()[i]
            if state == 'GEOGRAFI':
                if currseg.type.__unicode__() == u'G':
                    landskap.append(Landskap(currseg.d))
                else: # Sort and flush
                    sorted_landskap = sorted(landskap, Landskap.cmp)
                    landskap = []
                    for ls in sorted_landskap:
                        currmoment2.append(Segment(gtype, ls.abbrev))
                    currmoment2.append(Segment(currseg.type, currseg.d))
                    state = 'INITIAL'
            else:
                if currseg.type.__unicode__() == u'M1':
                    currmoment1.append(currmoment2)
                    self.segments.append(currmoment1)
                    currmoment1 = []
                    currmoment2 = []
                elif currseg.type.__unicode__() == u'M2':
                    currmoment1.append(currmoment2)
                    currmoment2 = []
                elif currseg.type.__unicode__() == u'G':
                    gtype = currseg.type
                    state = 'GEOGRAFI'
                    landskap = [Landskap(currseg.d)]
                elif currseg.type.__unicode__() == u'VH':
                    currmoment2.append(Segment(currseg.type, '['))
                elif currseg.type.__unicode__() == u'HH':
                    currmoment2.append(Segment(currseg.type, ']'))
                elif currseg.type.__unicode__() == u'VR':
                    currmoment2.append(Segment(currseg.type, '('))
                elif currseg.type.__unicode__() == u'HR':
                    currmoment2.append(Segment(currseg.type, ')'))
                else:
                    subsegs = re.split(ur'¶', currseg.d)
                    if len(subsegs) == 1:
                        currmoment2.append(Segment(currseg.type, subsegs[0]))
                    else:
                        maintype = currseg.type
                        currmoment2.append(Segment(maintype, subsegs[0]))
                        for j in range(1, len(subsegs)):
                            i += 1
                            subseg = self.raw_data_set().all()[i]
                            currmoment2.append(Segment(subseg.type, subseg.d))
                            if subsegs[j]:
                                currmoment2.append(Segment(maintype, subsegs[j]))
            i += 1
        currmoment1.append(currmoment2)
        self.segments.append(currmoment1)

    def resolve_moments(self, segment):
        if segment.ism1():
            if len(self.moments['M2']) > 1:
                for m2 in range(len(self.moments['M2'])):
                    self.moments['M2'][m2].text = '%c' % (97 + m2)
                    self.moments['M2'][m2].display = True
            self.moments['M2'] = []
            self.moments['M1'].append(segment)
        elif segment.ism2():
            self.moments['M2'].append(segment)

    def append_segment(self, data):
        segment = Segment(data)
        self.resolve_moments(segment)
        self.new_segments.append(segment)

    def collect(self):
        self.new_segments = []
        i = 0
        state = 'INITIAL'
        self.moments = { 'M1': [], 'M2': [] }
        while i < self.raw_data_set().count():
            currdat = self.raw_data_set().all()[i]
            if state == 'GEOGRAFI':
                if currdat.isgeo():
                    landskap.append(Landskap(currdat.d))
                else:
                    sorted_landskap = sorted(landskap, Landskap.cmp)
                    for ls in sorted_landskap:
                       self.new_segments.append(Segment(geotype, ls.abbrev))
                    self.append_segment(currdat)
                    state = 'INITIAL'
            else:
                if currdat.isgeo():
                    landskap = [Landskap(currdat.d)]
                    geotype = currdat.type
                    state = 'GEOGRAFI'
                else:
                    bits = re.split(ur'¶', currdat.d)
                    if len(bits) == 1:
                        self.append_segment(currdat)
                    else:
                        maintype = currdat.type
                        self.new_segments.append(Segment(maintype, bits[0]))
                        for bit in bits:
                            if bits.index(bit) > 0:
                                i += 1
                                self.new_segments.append(Segment(self.raw_data_set().all()[i]))
                            if bit:
                                self.new_segments.append(Segment(maintype, bit))
            i += 1
        if len(self.moments['M1']) > 1:
            for m1 in range(len(self.moments['M1'])):
                self.moments['M1'][m1].text = '%d' % (m1 + 1)
                self.moments['M1'][m1].display = True
        if len(self.moments['M2']) > 1:
            for m2 in range(len(self.moments['M2'])):
                self.moments['M2'][m2].text = '%c' % (96 + m2)
                self.moments['M2'][m2].display = True
        self.moments = { 'M1': [], 'M2': [] }

    def process(self, outfile):
        self.resolve_pilcrow()
        outfile.write(('\\hskip-1em\\SDL:SO{%s} ' % self.lemma).encode('UTF-8'))
        prevseg = self.segments[0][0][0]
        for m1 in range(len(self.segments)):
            moment1 = self.segments[m1]
            if m1 > 0 and len(self.segments) > 1:
                sec = Segment('M1', '%d' % m1)
                if prevseg:
                    prevseg.output(outfile, sec)
                prevseg = sec
            for m2 in range(len(moment1)):
                moment2 = moment1[m2]
                if m2 > 0 and len(moment1) > 1:
                    outfile.write('\SDL:M2{%c} ' % (96 + m2))
                    sec = Segment('M2', '%c' % (96 + m2))
                    if prevseg:
                        prevseg.output(outfile, sec)
                    prevseg = sec
                for seg in moment2:
                    if prevseg:
                        prevseg.output(outfile, seg)
                    prevseg = seg
                prevseg.output(outfile, prevseg) # FIXME Remove potential final space
        outfile.write("\n")

class Segment():
    def __init__(self, type, text = None):
        self.display = None
        if text:
            self.type = type
            self.text = text
        else: # type is actually a Data object
            self.type = type.type
            self.text = type.d

    def __str__(self):
        return self.type.__str__() + ' ' + self.text

    def __unicode__(self):
        return self.type.__unicode__() + ' ' + self.text

    def isgeo(self):
        return self.type.isgeo()

    def isrightdelim(self):
        if type(self.type) == 'unicode':
            return self.type in ['vh', 'hh', 'vr', 'hr']
        else:
            return self.type.isrightdelim()

    def ismoment(self):
        return self.ism1() or self.ism2()

    def ism1(self):
        return self.type.ism1()

    def ism2(self):
        return self.type.ism2()

    def output(self, outfile, next):
        outfile.write(('\SDL:%s{' % self.type.__unicode__()).encode('UTF-8'))
        outfile.write(self.text.replace(u'\\', '\\backslash ').encode('UTF-8'))
        outfile.write('}')
        if not next.isrightdelim():
            outfile.write(' ')

    # TODO Method hyphornot()

    def format(self):
        if self.type.__unicode__() == 'VH':
            return '['
        elif self.type.__unicode__() == 'HH':
            return ']'
        elif self.type.__unicode__() == 'VR':
            return '('
        elif self.type.__unicode__() == 'HR':
            return ')'
        else:
            return self.text.strip()

class Type(models.Model):
    abbrev = models.CharField(max_length = 5)
    name = models.CharField(max_length = 30)

    def __str__(self):
        return self.abbrev.upper()

    def __unicode__(self):
        return self.abbrev.upper()

    def isgeo(self):
        return self.abbrev == 'g'

    def isrightdelim(self):
        return self.abbrev in ['hh', 'hr', 'ip']

    def ismoment(self):
        return self.ism1() or self.ism2()

    def ism1(self):
        return self.abbrev == 'm1'

    def ism2(self):
        return self.abbrev == 'm2'

    def format(self):
        out = self.__unicode__()
        out += (4 - len(out)) * '\xa0'
        return out

class Data(models.Model):
    d = models.CharField(max_length = 2000)
    pos = models.SmallIntegerField()
    lemma = models.ForeignKey(Lemma)
    type = models.ForeignKey(Type)

    def __str__(self):
        return self.type.__str__() + ' ' + self.d

    def __unicode__(self):
        return self.type.__unicode__() + ' ' + self.d

    def webstyle(self):
        self.webstyles[self.type.__unicode__()]

    def printstyle(self):
        self.printstyles[self.type.__unicode__()]

    def isgeo(self):
        return self.type.isgeo()

class Landskap():
    ordning = [
        u'Skåne', u'Blek', u'Öland', u'Smål', u'Hall', u'Västg', u'Boh', u'Dalsl', u'Gotl', u'Östg', # 0-9
        u'Götal', # 10
        u'Sörml', u'Närke', u'Värml', u'Uppl', u'Västm', u'Dal', # 11 - 16
        u'Sveal', # 17
        u'Gästr', u'Häls', u'Härj', u'Med', u'Jämtl', u'Ång', u'Västb', u'Lappl', u'Norrb', # 18 - 26
        u'Norrl', # 27
    ]

    def cmp(self, other):
        if self.abbrev in self.ordning and other.abbrev in self.ordning:
            return cmp(self.ordning.index(self.abbrev), self.ordning.index(other.abbrev))
        else:
            return 0

    def __init__(self, abbrev):
        self.abbrev = abbrev.capitalize()

    def __str__(self):
        return self.abbrev

    def __unicode__(self):
        return self.abbrev

class Lexicon():
    def process(self):
        tempdir = mkdtemp('', 'SDL')
        source = file(tempdir + '/sdl.tex', 'w')
        source.write("""
            \starttext
            {\\tfc\\hfill Sveriges dialektlexikon\\hfill}

            {\\tfb\\hfill utgiven av Institutet för språk och folkminnen\\hfill}
        """.encode('UTF-8'))
        for lemma in Lemma.objects.filter(id__gt = 0).order_by('lemma'):
            print(lemma.lemma)
            lemma.process(source)
        source.close()

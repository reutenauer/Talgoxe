# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

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
        while i < self.raw_data_set().count():
            currseg = self.raw_data_set().all()[i]
            if currseg.type.__unicode__() == u'M1':
                currmoment1.append(currmoment2)
                self.segments.append(currmoment1)
                currmoment1 = []
                currmoment2 = []
            elif currseg.type.__unicode__() == u'M2':
                currmoment1.append(currmoment2)
                currmoment2 = []
            elif currseg.type.__unicode__() == u'G':
                currmoment2.append(Segment(currseg.type, currseg.d.capitalize()))
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
                        currmoment2.append(Segment(maintype, subsegs[j]))
            i += 1
        currmoment1.append(currmoment2)
        self.segments.append(currmoment1)

class Segment():
    def __init__(self, type, text):
        self.type = type
        self.text = text

    def __str__(self):
        return self.type.__str__() + ' ' + self.text

    def __unicode__(self):
        return self.type.__unicode__() + ' ' + self.text

class Type(models.Model):
    abbrev = models.CharField(max_length = 5)
    name = models.CharField(max_length = 30)

    def __str__(self):
        return self.abbrev.upper()

    def __unicode__(self):
        return self.abbrev.upper()

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

    def format(self):
        return d.strip()

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

    def resolve_pilcrow(self):
        i = 0
        self.raw_data_set = self.data_set.filter(id__gt = 0).order_by('pos')
        while i < len(self.raw_data_set.count()):
            currseg = self.raw_data_set.all()[i]
            subsegs = re.split(ur'¶', currseg)
            if len(subsegs) == 1:
                self.segments.append(subsegs[0])
            else:
                seginprogress = subsegs[0]
                for j in range(1, len(subsegs)):
                    i += 1
                    seginprogress += self.raw_data_set.all()[i] + subsegs[j]
                self.segments.append(seginprogress)

class Type(models.Model):
    abbrev = models.CharField(max_length = 5)
    name = models.CharField(max_length = 30)

    def __str__(self):
        return self.abbrev.upper()

    def __unicode__(self):
        return self.abbrev.upper()

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

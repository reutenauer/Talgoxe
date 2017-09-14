# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

# Not using migration; instead dump the SQL, remove the AUTO_INCREMENT FROM primary keys,
# and copy the existing table into them.  For Data (table fdata), this is needed:
# INSERT INTO talgoxe_data (id, d, pos, lemma_id, type_id) SELECT d_id, d, pos, l_id, typ FROM fdata WHERE typ IN (SELECT nr FROM typer) AND l_id IN (SELECT l_id FROM lemma);
# Foreign keys fails otherwise!
class Lemma(models.Model):
    lemma = models.CharField(max_length = 100)

    def __str__(self):
        return self.lemma

    def __unicode__(self):
        return self.lemma

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

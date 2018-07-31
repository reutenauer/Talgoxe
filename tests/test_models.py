from os import popen
from os.path import abspath, dirname, join

from django.test import TestCase

from talgoxe.models import Artikel, Typ, Spole, Landskap, Exporter

class ArtikelTestCase(TestCase):
    def setUp(self):
        self.sotyp = Typ.objects.create(kod = 'so')
        self.sovtyp = Typ.objects.create(kod = 'sov')
        self.oktyp = Typ.objects.create(kod = 'ok')
        self.m1typ = Typ.objects.create(kod = 'm1')
        self.betyp = Typ.objects.create(kod = 'be')
        self.gtyp = Typ.objects.create(kod = 'g')
        self.iptyp = Typ.objects.create(kod = 'ip')

    def dump_artikel(self, artikel):
        dump = ''
        artikel.collect()
        for fjäder in artikel.fjädrar:
            dump += fjäder.typ.upper() + ' ' + fjäder.text + ' '

        return dump

    def test_so_sov(self):
        artikel = Artikel.objects.create(lemma = 'fabbel', rang = 0)

        Spole.objects.create(typ = self.oktyp, text = 'm.', artikel = artikel, pos = 0)
        Spole.objects.create(typ = self.oktyp, text = 'n.', artikel = artikel, pos = 1)
        artikel.collect()
        self.assertEqual(4, len(artikel.fjädrar))
        self.assertEqual('el.', artikel.fjädrar[2].text)

    def test_dagom(self):
        artikel = Artikel.objects.create(lemma = 'dagom', rang = 0)
        Spole.objects.create(typ = self.oktyp, text = 'adv.', artikel = artikel, pos = 0)
        Spole.objects.create(typ = self.m1typ, text = '', artikel = artikel, pos = 1)
        Spole.objects.create(typ = self.betyp, text = 'dagligen', artikel = artikel, pos = 2)
        Spole.objects.create(typ = self.gtyp , text = 'gotl', artikel = artikel, pos = 3)
        Spole.objects.create(typ = self.iptyp, text = '.', artikel = artikel, pos = 4)
        artikel.collect()
        self.assertEqual(6, len(artikel.fjädrar))
        self.assertEqual('SOV dagom OK adv. M1  BE dagligen G Gotl IP . ', self.dump_artikel(artikel))

    def test_överflödig_fjäder(self):
        pass # TODO Skriv; jfr. kommit 78a9797

    def test_första_fjädern_är_so(self):
        artikel = Artikel.objects.create(lemma = 'dagom', rang = 0)
        Spole.objects.create(typ = self.betyp, text = 'dagligen', artikel = artikel, pos = 0)
        artikel.collect()
        self.assertEqual(2, len(artikel.fjädrar))
        self.assertEqual('dagom', artikel.fjädrar[0].text)

class LandskapTestCase(TestCase):
    def setUp(self):
        self.landskap0 = Landskap('Norrb')
        self.landskap1 = Landskap('Östg')

    def till_landskap(self, namn):
        return list(map(lambda namn: Landskap(namn), namn))

    def från_landskap(self, landskap):
        return list(map(lambda landskap: landskap.abbrev, landskap))

    def test_landskapens_ordning(self):
        sorterade_landskap = sorted([self.landskap0, self.landskap1], key = Landskap.key)
        self.assertEqual(sorterade_landskap[0], self.landskap1)
        self.assertEqual(sorterade_landskap[1], self.landskap0)

    def test_reduce_landskap(self):
        input = [Landskap('Skåne'), Landskap('Blek'), Landskap('Öland'), Landskap('Smål'),
          Landskap('Hall'), Landskap('Västg'), Landskap('Boh'), Landskap('Dalsl')]
        self.assertEqual(Landskap.reduce(input)[0].abbrev, 'Götal')

    def test_that_reduce_landskap_also_sorts(self):
        bokstavsordningssorterade = [Landskap('Blek'), Landskap('Dalsl'), Landskap('Skåne'), Landskap('Smål'), Landskap('Västg')]
        self.assertEqual(list(map(lambda ls: ls.abbrev, Landskap.reduce(bokstavsordningssorterade))), ['Skåne', 'Blek', 'Smål', 'Västg', 'Dalsl'])

    def test_ett_mer_komplicerat_fall(self):
        landskap = self.till_landskap(['Blek', 'Gotl', 'Dal' ,'Gästr', 'Norrb',
          'Närke', 'Skåne', 'Smål', 'Sörml', 'Västg', 'Värml', 'Ång', 'Östg'])
        namn = self.från_landskap(Landskap.reduce(landskap))
        self.assertEqual(namn, ['Skåne', 'Blek', 'Smål', 'Västg', 'Gotl',
          'Östg', 'Sveal', 'Gästr', 'Ång', 'Norrb'])

    def test_ett_komplet_fall(self):
        landskap = self.till_landskap(['Blek', 'Boh', 'Dal', 'Dalsl', 'Gästr', 'Häls', 'Jämtl',
          'Lappl', 'Norrb', 'Närke', 'Smål', 'Sörml', 'Uppl',
          'Värml', 'Västb', 'Västg', 'Västm', 'Öland', 'Östg'])
        namn = self.från_landskap(Landskap.reduce(landskap))
        self.assertEqual(namn, ['Götal', 'Sveal', 'Norrl'])

class ExporterTestCase(TestCase):
    def setUp(self):
        betyp = Typ.objects.create(kod = 'be')
        Typ.objects.create(kod = 'sov')
        Typ.objects.create(kod = 'ok')
        self.dagom = Artikel.objects.create(lemma = 'dagom', rang = 0)
        Spole.objects.create(typ = betyp, text = 'a', artikel = self.dagom, pos = 0)
        Spole.objects.create(typ = betyp, text = 'b', artikel = self.dagom, pos = 1)
        Spole.objects.create(typ = betyp, text = 'c', artikel = self.dagom, pos = 2)

    def generic_export_test(self, format, expectedFileType):
        exporter = Exporter(format)
        filepath = exporter.export([self.dagom.id])
        fileabspath = join(abspath(dirname(__file__)), '..', 'talgoxe', 'static', filepath)
        filetype = popen('file %s' % fileabspath).read().split(':')[1].strip()
        self.assertEqual(expectedFileType, filetype)

    def test_pdf_export(self):
        self.generic_export_test("pdf", 'PDF document, version 1.7')

    def test_odf_export(self):
        self.generic_export_test("odt", 'OpenDocument Text')

    def test_docx_export(self):
        self.generic_export_test('docx', 'Microsoft OOXML')

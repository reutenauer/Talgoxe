from django.test import TestCase
from talgoxe.models import Artikel, Typ, Spole, Landskap

class ArtikelTestCase(TestCase):
    def setUp(self):
        Typ.objects.create(kod = 'so')

    def test_so_sov(self):
        artikel = Artikel.objects.create(lemma = 'fabbel', rang = 0)
        oktyp = Typ.objects.create(kod = 'ok')
        Spole.objects.create(typ = oktyp, text = 'm.', artikel = artikel, pos = 0)
        Spole.objects.create(typ = oktyp, text = 'n.', artikel = artikel, pos = 1)
        artikel.collect()
        # list(map(lambda fjäder: print(fjäder), artikel.fjädrar))
        for fjäder in artikel.fjädrar:
            print(fjäder.typ, fjäder.text)
        self.assertEqual(3, len(artikel.fjädrar))
        self.assertEqual('el.', artikel.fjädrar[1].text)

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

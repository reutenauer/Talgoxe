from django.test import TestCase
from talgoxe.models import Landskap

class LandskapTestCase(TestCase):
  def setUp(self):
      self.landskap0 = Landskap('Norrb')
      self.landskap1 = Landskap('Östg')

  def test_landskapens_ordning(self):
      sorterade_landskap = sorted([self.landskap0, self.landskap1], key = Landskap.key)
      self.assertEqual(sorterade_landskap[0], self.landskap1)
      self.assertEqual(sorterade_landskap[1], self.landskap0)

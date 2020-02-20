from django.test import TestCase
from .apps import CoreConfig

# Create your tests here.


class TestModel(TestCase):
    def testModel(self):
        app = CoreConfig.name
        self.assertEqual(app, 'core')

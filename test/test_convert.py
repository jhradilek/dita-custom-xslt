import unittest
from src.dita import convert

class TestDitaConvert(unittest.TestCase):
    def test_name_exposed(self):
        self.assertIsInstance(convert.NAME, str)
        self.assertNotEqual(convert.NAME, '')

    def test_version_exposed(self):
        self.assertIsInstance(convert.VERSION, str)
        self.assertNotEqual(convert.VERSION, '')

    def test_description_exposed(self):
        self.assertIsInstance(convert.DESCRIPTION, str)
        self.assertNotEqual(convert.DESCRIPTION, '')

    def test_to_concept_exposed(self):
        self.assertTrue(hasattr(convert, 'to_concept'))

    def test_to_reference_exposed(self):
        self.assertTrue(hasattr(convert, 'to_reference'))

    def test_to_task_exposed(self):
        self.assertTrue(hasattr(convert, 'to_task'))

    def test_to_task_generated_exposed(self):
        self.assertTrue(hasattr(convert, 'to_task_generated'))

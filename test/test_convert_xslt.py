import unittest
from pathlib import PurePath
from src.dita.convert import xslt

class TestDitaConvertXSLT(unittest.TestCase):
    def test_concept_returns_path(self):
        self.assertIsInstance(xslt.concept, PurePath)

    def test_concept_returns_file(self):
        self.assertTrue(xslt.concept.is_file())

    def test_reference_returns_path(self):
        self.assertIsInstance(xslt.reference, PurePath)

    def test_reference_returns_file(self):
        self.assertTrue(xslt.reference.is_file())

    def test_task_returns_path(self):
        self.assertIsInstance(xslt.task, PurePath)

    def test_task_returns_file(self):
        self.assertTrue(xslt.task.is_file())

    def test_concept_generated_returns_path(self):
        self.assertIsInstance(xslt.concept_generated, PurePath)

    def test_concept_generated_returns_file(self):
        self.assertTrue(xslt.concept_generated.is_file())

    def test_reference_generated_returns_path(self):
        self.assertIsInstance(xslt.reference_generated, PurePath)

    def test_reference_generated_returns_file(self):
        self.assertTrue(xslt.reference_generated.is_file())

    def test_task_generated_returns_path(self):
        self.assertIsInstance(xslt.task_generated, PurePath)

    def test_task_generated_returns_file(self):
        self.assertTrue(xslt.task_generated.is_file())

    def test_single_topic_returns_path(self):
        self.assertIsInstance(xslt.single_topic, PurePath)

    def test_single_topic_returns_file(self):
        self.assertTrue(xslt.single_topic.is_file())

    def test_single_map_returns_path(self):
        self.assertIsInstance(xslt.single_map, PurePath)

    def test_single_map_returns_file(self):
        self.assertTrue(xslt.single_map.is_file())

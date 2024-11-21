import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertTransform(unittest.TestCase):
    def test_to_concept_returns_result(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-concept">
            <title>Topic title</title>
        </topic>
        '''))

        self.assertIsInstance(transform.to_concept(xml), etree._XSLTResultTree)

    def test_to_reference_returns_result(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-concept">
            <title>Topic title</title>
        </topic>
        '''))

        self.assertIsInstance(transform.to_reference(xml), etree._XSLTResultTree)

    def test_to_task_returns_result(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-concept">
            <title>Topic title</title>
        </topic>
        '''))

        self.assertIsInstance(transform.to_task(xml), etree._XSLTResultTree)

    def test_to_task_generated_returns_result(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-concept">
            <title>Topic title</title>
        </topic>
        '''))

        self.assertIsInstance(transform.to_task_generated(xml), etree._XSLTResultTree)

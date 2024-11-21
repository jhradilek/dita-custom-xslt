import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToConcept(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <concept id="example-concept">
            <title>Concept title</title>
        </concept>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_concept(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_concept_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic body</p>
            </body>
        </topic>
        '''))

        concept = transform.to_concept(xml)

        self.assertEqual(concept.docinfo.xml_version, '1.0')
        self.assertEqual(concept.docinfo.public_id, '-//OASIS//DTD DITA Concept//EN')
        self.assertEqual(concept.docinfo.system_url, 'concept.dtd')

        self.assertTrue(concept.xpath('boolean(/concept)'))
        self.assertTrue(concept.xpath('boolean(/concept[@id="example-topic"])'))
        self.assertTrue(concept.xpath('boolean(/concept/title[text()="Topic title"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody)'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic body"])'))

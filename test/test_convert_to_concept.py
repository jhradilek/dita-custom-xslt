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

    def test_incomplete_dl(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <dl>
                    <dlentry>
                        <dt>First term</dt>
                        <dt>Second term</dt>
                    </dlentry>
                </dl>
            </body>
        </topic>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_concept(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Incomplete definition list')

    def test_concept_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>First paragraph</p>
                <example>
                    <p>First example</p>
                </example>
                <p>Second paragraph</p>
                <p>Third paragraph</p>
                <example>
                    <p>Second example</p>
                </example>
                <section>
                    <p>First section</p>
                </section>
                <p>Fourth paragraph</p>
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
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="First paragraph"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/example[1]/p[text()="First example"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/section[1]/p[1][text()="Second paragraph"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/section[1]/p[2][text()="Third paragraph"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/example[2]/p[text()="Second example"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/section[2]/p[text()="First section"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/section[3]/p[text()="Fourth paragraph"])'))

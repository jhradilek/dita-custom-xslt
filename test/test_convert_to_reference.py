import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToReference(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <reference id="example-concept">
            <title>Reference title</title>
        </reference>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_reference(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_reference_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic body</p>
            </body>
        </topic>
        '''))

        reference = transform.to_reference(xml)

        self.assertEqual(reference.docinfo.xml_version, '1.0')
        self.assertEqual(reference.docinfo.public_id, '-//OASIS//DTD DITA Reference//EN')
        self.assertEqual(reference.docinfo.system_url, 'reference.dtd')

        self.assertTrue(reference.xpath('boolean(/reference)'))
        self.assertTrue(reference.xpath('boolean(/reference[@id="example-topic"])'))
        self.assertTrue(reference.xpath('boolean(/reference/title[text()="Topic title"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody)'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section)'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic body"])'))

import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToSingleMap(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <task id="example-task">
            <title>Task title</title>
        </task>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_single_map(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_single_map_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic" outputclass="assembly">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
            </body>
            <topic id="first-section" outputclass="task">
                <title>First section title</title>
                <body>
                    <p>First section body</p>
                </body>
            </topic>
            <topic id="second-section" outputclass="concept">
                <title>Second section title</title>
                <body>
                    <p>Second section body</p>
                </body>
                <topic id="third-section" outputclass="reference">
                    <title>Third section title</title>
                    <body>
                        <p>Third section body</p>
                    </body>
                </topic>
            </topic>
        </topic>
        '''))

        ditamap = transform.to_single_map(xml)

        self.assertEqual(ditamap.docinfo.xml_version, '1.0')
        self.assertEqual(ditamap.docinfo.public_id, '-//OASIS//DTD DITA Map//EN')
        self.assertEqual(ditamap.docinfo.system_url, 'map.dtd')

        self.assertTrue(ditamap.xpath('boolean(/map)'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref[@type="concept"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref[@href="example-topic.dita"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref/topicref[1][@type="task"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref/topicref[1][@href="first-section.dita"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref/topicref[2][@type="concept"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref/topicref[2][@href="second-section.dita"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref/topicref[2]/topicref[@type="reference"])'))
        self.assertTrue(ditamap.xpath('boolean(/map/topicref/topicref[2]/topicref[@href="third-section.dita"])'))

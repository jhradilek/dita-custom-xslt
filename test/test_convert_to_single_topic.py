import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToSingleTopic(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <task id="example-task">
            <title>Task title</title>
        </task>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_single_topic(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_single_topic_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <section id="first-section-id">
                    <title>First section title</title>
                    <p>First section body</p>
                </section>
                <section id="second-section-id">
                    <title>Second section title</title>
                    <p>Second section body</p>
                    <section id="third-section-id">
                        <title>Third section title</title>
                        <p>Third section body</p>
                    </section>
                </section>
            </body>
        </topic>
        '''))

        topic = transform.to_single_topic(xml)

        self.assertEqual(topic.docinfo.xml_version, '1.0')
        self.assertEqual(topic.docinfo.public_id, '-//OASIS//DTD DITA Topic//EN')
        self.assertEqual(topic.docinfo.system_url, 'topic.dtd')

        self.assertTrue(topic.xpath('boolean(/topic)'))
        self.assertTrue(topic.xpath('boolean(/topic[@id="example-topic"])'))
        self.assertTrue(topic.xpath('boolean(/topic/title[text()="Topic title"])'))
        self.assertTrue(topic.xpath('boolean(/topic/body)'))
        self.assertTrue(topic.xpath('boolean(/topic/body/p[text()="Topic introduction"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[1])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[1][@id="first-section-id"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[1]/title[text()="First section title"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[1]/body)'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[1]/body/p[text()="First section body"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[2])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[2][@id="second-section-id"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[2]/title[text()="Second section title"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[2]/body)'))
        self.assertTrue(topic.xpath('boolean(/topic/topic[2]/body/p[text()="Second section body"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic/topic)'))
        self.assertTrue(topic.xpath('boolean(/topic/topic/topic[@id="third-section-id"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic/topic/title[text()="Third section title"])'))
        self.assertTrue(topic.xpath('boolean(/topic/topic/topic/body)'))
        self.assertTrue(topic.xpath('boolean(/topic/topic/topic/body/p[text()="Third section body"])'))

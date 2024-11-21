import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertTransform(unittest.TestCase):
    def test_to_concept_requires_topic(self):
        xml = etree.parse(StringIO('''\
        <concept id="example-concept">
            <title>Concept title</title>
        </concept>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_concept(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_to_concept_transforms_topic(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic body</p>
            </body>
        </topic>
        '''))

        concept = transform.to_concept(xml)

        self.assertTrue(concept.xpath('boolean(/concept)'))
        self.assertTrue(concept.xpath('boolean(/concept[@id="example-topic"])'))
        self.assertTrue(concept.xpath('boolean(/concept/title[text()="Topic title"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody)'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic body"])'))

    def test_to_reference_requires_topic(self):
        xml = etree.parse(StringIO('''\
        <reference id="example-concept">
            <title>Reference title</title>
        </reference>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_reference(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_to_reference_transforms_topic(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic body</p>
            </body>
        </topic>
        '''))

        reference = transform.to_reference(xml)

        self.assertTrue(reference.xpath('boolean(/reference)'))
        self.assertTrue(reference.xpath('boolean(/reference[@id="example-topic"])'))
        self.assertTrue(reference.xpath('boolean(/reference/title[text()="Topic title"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody)'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section)'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic body"])'))

    def test_to_task_requires_topic(self):
        xml = etree.parse(StringIO('''\
        <task id="example-concept">
            <title>Task title</title>
        </task>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_to_task_forbids_sections(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <section>
                    <title>Section title</title>
                    <p>Section body</p>
                </section>
            </body>
        </topic>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Section not allowed in a DITA task')

    def test_to_task_generated_requires_topic(self):
        xml = etree.parse(StringIO('''\
        <task id="example-concept">
            <title>Task title</title>
        </task>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task_generated(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_to_task_generated_forbids_sections(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <section>
                    <title>Section title</title>
                    <p>Section body</p>
                </section>
            </body>
        </topic>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task_generated(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Section not allowed in a DITA task')

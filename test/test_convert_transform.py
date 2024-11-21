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

    def test_to_task_transforms_topic(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <ol>
                    <li>First step</li>
                    <li>Second step</li>
                </ol>
                <p>Topic summary</p>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(/task)'))
        self.assertTrue(task.xpath('boolean(/task[@id="example-topic"])'))
        self.assertTrue(task.xpath('boolean(/task/title[text()="Topic title"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody)'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step[1]/cmd[text()="First step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step[2]/cmd[text()="Second step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/p[text()="Topic summary"])'))

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

    def test_to_task_generated_transforms_topic(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Prerequisites</b></p>
                <ul>
                    <li>First prerequisite</li>
                    <li>Second prerequisite</li>
                </ul>
                <p outputclass="title"><b>Procedure</b></p>
                <ol>
                    <li>First step</li>
                    <li>Second step</li>
                </ol>
                <p outputclass="title"><b>Verification</b></p>
                <ul>
                    <li>Verification step</li>
                </ul>
                <p outputclass="title"><b>Troubleshooting</b></p>
                <ol>
                    <li>First troubleshooting step</li>
                    <li>Second troubleshooting step</li>
                </ol>
                <p outputclass="title"><b>Next steps</b></p>
                <ul>
                    <li>Next step</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task)'))
        self.assertTrue(task.xpath('boolean(/task[@id="example-topic"])'))
        self.assertTrue(task.xpath('boolean(/task/title[text()="Topic title"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody)'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/prereq/ul/li[1][text()="First prerequisite"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/prereq/ul/li[2][text()="Second prerequisite"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step[1]/cmd[text()="First step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step[2]/cmd[text()="Second step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/ul/li[1][text()="Verification step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/tasktroubleshooting/ol/li[1][text()="First troubleshooting step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/tasktroubleshooting/ol/li[2][text()="Second troubleshooting step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/postreq/ul/li[1][text()="Next step"])'))

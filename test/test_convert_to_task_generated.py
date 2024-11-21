import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToTaskGenerated(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <task id="example-concept">
            <title>Task title</title>
        </task>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task_generated(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_sections_not_permitted(self):
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

    def test_task_structure(self):
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

        self.assertEqual(task.docinfo.xml_version, '1.0')
        self.assertEqual(task.docinfo.public_id, '-//OASIS//DTD DITA Task//EN')
        self.assertEqual(task.docinfo.system_url, 'task.dtd')

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

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

    def test_unsupported_titles(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Unsupported title</b></p>
                <p>Unsupported content</p>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, "WARNING: Unsupported title 'Unsupported title' found, skipping...")

        self.assertFalse(task.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported title"])'))
        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_nonlist_elements(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Procedure</b></p>
                <p>Unsupported content</p>
                <ol>
                    <li>Task step</li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, "WARNING: Non-list elements found in steps, skipping...")

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))

    def test_extra_list_elements(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Procedure</b></p>
                <ol>
                    <li>Task step</li>
                </ol>
                <ol>
                    <li>Unsupported content</li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, "WARNING: Extra list elements found in steps, skipping...")

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))

    def test_no_list_elements(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Procedure</b></p>
                <p>Unsupported content</p>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertIn('WARNING: No list elements found in steps', [m.message for m in err])

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_task_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Prerequisites</b></p>
                <ul>
                    <li>Task prerequisite</li>
                </ul>
                <p outputclass="title"><b>Procedure</b></p>
                <ol>
                    <li>Task step</li>
                </ol>
                <p outputclass="title"><b>Verification</b></p>
                <ul>
                    <li>Verification step</li>
                </ul>
                <p outputclass="title"><b>Troubleshooting</b></p>
                <ol>
                    <li>Troubleshooting step</li>
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
        self.assertTrue(task.xpath('boolean(/task/taskbody/prereq/ul/li[text()="Task prerequisite"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/ul/li[text()="Verification step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/tasktroubleshooting/ol/li[text()="Troubleshooting step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/postreq/ul/li[text()="Next step"])'))
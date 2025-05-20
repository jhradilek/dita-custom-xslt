import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToTask(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <task id="example-concept">
            <title>Task title</title>
        </task>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task(xml)

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
            transform.to_task(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Section not allowed in a DITA task')

    def test_multiple_examples_not_permitted(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <example>
                    <p>A supported example.</p>
                </example>
                <example>
                    <p>An unsupported example.</p>
                </example>
            </body>
        </topic>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_task(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Multiple examples not allowed in a DITA task')

    def test_task_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <ol>
                    <li>Task step</li>
                </ol>
                <p>Topic summary</p>
                <example>
                    <p>Example</p>
                </example>
                <p>Next step</p>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertEqual(task.docinfo.xml_version, '1.0')
        self.assertEqual(task.docinfo.public_id, '-//OASIS//DTD DITA Task//EN')
        self.assertEqual(task.docinfo.system_url, 'task.dtd')

        self.assertTrue(task.xpath('boolean(/task)'))
        self.assertTrue(task.xpath('boolean(/task[@id="example-topic"])'))
        self.assertTrue(task.xpath('boolean(/task/title[text()="Topic title"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody)'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/p[text()="Topic summary"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/example/p[text()="Example"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/postreq/p[text()="Next step"])'))

    def test_context_without_steps(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <example>
                    <p>Example</p>
                </example>
                <p>Next step</p>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/context/p[text()="Next step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/example/p[text()="Example"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/steps)'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/result)'))

    def test_context_without_example(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p>Next step</p>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Next step"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/steps)'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/result)'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/example)'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/postreq)'))

    def test_result_without_example(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <ol>
                    <li>Task step</li>
                </ol>
                <p>Topic summary</p>
                <p>Next step</p>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertFalse(task.xpath('boolean(/task/taskbody/result/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/p[text()="Topic summary"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/p[text()="Next step"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/example)'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/postreq)'))

    def test_task_step_info(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <ol>
                    <li>
                        <p>Step introduction</p>
                        <codeblock>Step code</codeblock>
                        <p>Step explanation</p>
                    </li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/p[text()="Step explanation"])'))

    def test_task_substeps(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <ol>
                    <li>
                        <p>Step introduction</p>
                        <ol>
                            <li>
                                <p>Substep introduction</p>
                                <codeblock>Substep code</codeblock>
                                <p>Substep explanation</p>
                            </li>
                        </ol>
                    </li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/cmd[text()="Substep introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/info/codeblock[text()="Substep code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/info/p[text()="Substep explanation"])'))

    def test_alternating_substeps(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <ol>
                    <li>
                        <p>Step introduction</p>
                        <codeblock>Step code</codeblock>
                        <p>Step explanation</p>
                        <ol>
                            <li>First substeps</li>
                        </ol>
                        <p>Additional information</p>
                        <ol>
                            <li>Second substeps</li>
                        </ol>
                        <p>Step summary</p>
                    </li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[1]/p[text()="Step explanation"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[1]/substep/cmd[text()="First substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[2]/p[text()="Additional information"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[2]/substep/cmd[text()="Second substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[3]/p[text()="Step summary"])'))

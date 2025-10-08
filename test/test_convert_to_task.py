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

    def test_task_stepxmp(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <ol>
                    <li>
                        <p>Step introduction</p>
                        <codeblock>Step code</codeblock>
                        <example>Step example</example>
                    </li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[text()="Step example"])'))

    def test_alternating_stepxmp(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <ol>
                    <li>
                        <p>Step introduction</p>
                        <codeblock>Step code</codeblock>
                        <p>Step explanation</p>
                        <example>
                            <p>Example introduction</p>
                            <codeblock>Example code</codeblock>
                        </example>
                        <p>Additional information</p>
                        <example>Additional example</example>
                        <p>Step summary</p>
                    </li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[1]/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[1]/p[text()="Example introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[1]/codeblock[text()="Example code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[2]/p[text()="Additional information"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[2][text()="Additional example"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[3]/p[text()="Step summary"])'))

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
                            <li>
                                <p>First substeps</p>
                                <example>First substep example</example>
                            </li>
                        </ol>
                        <p>Additional information</p>
                        <ol>
                            <li>Second substeps</li>
                        </ol>
                        <example>Step example</example>
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
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[1]/substep/stepxmp[text()="First substep example"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[2]/p[text()="Additional information"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[2]/substep/cmd[text()="Second substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[text()="Step example"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[3]/p[text()="Step summary"])'))

    def test_universal_attributes(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <ol id="steps" props="persona(sysadmin)" base="arch(x86_64)" platform="linux mac" product="dita-convert" audience="novice" otherprops="pdf" deliveryTarget="pdf" importance="normal" rev="v1.0.0" status="new" translate="yes" xml:lang="en-us" dir="ltr" compact="yes">
                    <li id="first-step">
                        <p id="step-intro">Step introduction</p>
                        <ol id="substeps">
                            <li id="first-substep">
                                <p id="substep-intro">Substep introduction</p>
                                <codeblock>Substep code</codeblock>
                                <p>Substep explanation</p>
                                <example id="substep-example">Substep example</example>
                            </li>
                        </ol>
                    </li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task(xml)

        self.assertTrue(task.xpath('boolean(//steps[@id="steps"])'))
        self.assertTrue(task.xpath('boolean(//steps[@props="persona(sysadmin)"])'))
        self.assertTrue(task.xpath('boolean(//steps[@base="arch(x86_64)"])'))
        self.assertTrue(task.xpath('boolean(//steps[@platform="linux mac"])'))
        self.assertTrue(task.xpath('boolean(//steps[@product="dita-convert"])'))
        self.assertTrue(task.xpath('boolean(//steps[@audience="novice"])'))
        self.assertTrue(task.xpath('boolean(//steps[@otherprops="pdf"])'))
        self.assertTrue(task.xpath('boolean(//steps[@deliveryTarget="pdf"])'))
        self.assertTrue(task.xpath('boolean(//steps[@importance="normal"])'))
        self.assertTrue(task.xpath('boolean(//steps[@rev="v1.0.0"])'))
        self.assertTrue(task.xpath('boolean(//steps[@status="new"])'))
        self.assertTrue(task.xpath('boolean(//steps[@translate="yes"])'))
        self.assertTrue(task.xpath('boolean(//steps[@xml:lang="en-us"])'))
        self.assertTrue(task.xpath('boolean(//steps[@dir="ltr"])'))
        self.assertFalse(task.xpath('boolean(//steps/@compact)'))

        self.assertTrue(task.xpath('boolean(//steps[@id="steps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step[@id="first-step"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/cmd[@id="step-intro"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[@id="substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep[@id="first-substep"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/cmd[@id="substep-intro"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/stepxmp[@id="substep-example"])'))

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

    def test_section_in_procedure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
                <ol>
                    <li>A step.</li>
                </ol>
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

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, "WARNING: Unsupported title 'Unsupported title' found, skipping...")

        self.assertFalse(task.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported title"])'))
        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_multiple_examples(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <example>
                    <p>An example</p>
                </example>
                <example>
                    <p>Unsupported content</p>
                </example>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, "WARNING: Extra example elements found, skipping...")

        self.assertFalse(task.xpath('boolean(//example[2])'))
        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))

    def test_nonlist_elements_in_procedure(self):
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

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Non-list elements found in steps, skipping...')

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))

    def test_example_after_procedure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
                <ol>
                    <li>A step.</li>
                </ol>
                <example>
                    <title>Example title</title>
                    <p>An example</p>
                </example>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 0)

    def test_extra_list_elements_in_procedure(self):
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

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Extra list elements found in steps, skipping...')

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))

    def test_no_list_elements_in_procedure(self):
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

        self.assertNotEqual(len(err), 0)
        self.assertIn('WARNING: No list elements found in steps', [m.message for m in err])

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_nonlist_elements_in_related_links(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <p>Unsupported content</p>
                <ul>
                    <li><xref href="http://example.com" format="html" scope="external" /></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Non-list elements found in related links, skipping...')

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/related-links/link[@href="http://example.com"])'))

    def test_extra_list_elements_in_related_links(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li><xref href="http://example.com" format="html" scope="external" /></li>
                </ul>
                <ul>
                    <li>Unsupported content</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Extra list elements found in related-links, skipping...')

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/related-links/link[@href="http://example.com"])'))

    def test_no_list_elements_in_related_links(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <p>Unsupported content</p>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertNotEqual(len(err), 0)
        self.assertIn('WARNING: No list elements found in related links', [m.message for m in err])

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_text_node_in_related_links(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li>Unsupported content</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_other_node_in_related_links(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li><b>Unsupported content</b></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertFalse(task.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_multiple_links_in_related_links(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li><xref href="http://example.com" format="html" scope="external" /><xref href="http://example.com" format="html" scope="external" /></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)
        err  = transform.to_task_generated.error_log

        self.assertEqual(len(err), 1)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))

    def test_task_outputclass(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic" outputclass="procedure">
            <title outputclass="main">Topic title</title>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertFalse(task.xpath('boolean(/task/@outputclass)'))
        self.assertTrue(task.xpath('boolean(/task[@id="example-topic"])'))
        self.assertTrue(task.xpath('boolean(/task/title[@outputclass="main"])'))

    def test_task_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="abstract">Topic abstract</p>
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
                <example>
                    <p>Example</p>
                </example>
                <p outputclass="title"><b>Next step</b></p>
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
        self.assertTrue(task.xpath('boolean(/task/shortdesc[text()="Topic abstract"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody)'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/prereq/ul/li[text()="Task prerequisite"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/context/p[text()="Topic abstract"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/steps/step/cmd[text()="Task step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/result/ul/li[text()="Verification step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/tasktroubleshooting/ol/li[text()="Troubleshooting step"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/example/p[text()="Example"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/postreq/ul/li[text()="Next step"])'))

    def test_prerequisite(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Prerequisite</b></p>
                <ul>
                    <li>Task prerequisite</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/prereq/ul/li[text()="Task prerequisite"])'))

    def test_result(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Result</b></p>
                <ul>
                    <li>Verification step</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/result/ul/li[text()="Verification step"])'))

    def test_results(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Results</b></p>
                <ul>
                    <li>Verification step</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/result/ul/li[text()="Verification step"])'))

    def test_troubleshooting_step(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Troubleshooting step</b></p>
                <ol>
                    <li>Troubleshooting step</li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/tasktroubleshooting/ol/li[text()="Troubleshooting step"])'))

    def test_troubleshooting_steps(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Troubleshooting steps</b></p>
                <ol>
                    <li>Troubleshooting step</li>
                </ol>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/tasktroubleshooting/ol/li[text()="Troubleshooting step"])'))

    def test_example(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Troubleshooting steps</b></p>
                <example id="example-id">
                    <title>Example title</title>
                    <p>Example paragraph</p>
                </example>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/example[@id="example-id"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/example/title[text()="Example title"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/example/p[text()="Example paragraph"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/tasktroubleshooting/example)'))

    def test_next_steps(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="title"><b>Next steps</b></p>
                <ul>
                    <li>Next step</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/postreq/ul/li[text()="Next step"])'))

    def test_multiple_abstracts(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="abstract">Topic abstract</p>
                <p outputclass="abstract">Topic introduction</p>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/shortdesc[text()="Topic abstract"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[text()="Topic introduction"])'))
        self.assertFalse(task.xpath('boolean(/task/shortdesc[text()="Topic introduction"])'))
        self.assertFalse(task.xpath('boolean(/task/taskbody/context/p[text()="Topic abstract"])'))

    def test_misplaced_abstract(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p>Topic introduction</p>
                <p outputclass="abstract">Topic abstract</p>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[1][text()="Topic introduction"])'))
        self.assertTrue(task.xpath('boolean(/task/taskbody/context/p[2][text()="Topic abstract"])'))
        self.assertFalse(task.xpath('boolean(/task/shortdesc)'))

    def test_task_steps_unordered(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
                <ul>
                    <li>Unordered step</li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(//steps-unordered/step/cmd[text()="Unordered step"])'))

    def test_task_step_info(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
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

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/p[text()="Step explanation"])'))

    def test_task_stepxmp(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
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

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[text()="Step example"])'))

    def test_alternating_stepxmp(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
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

        task = transform.to_task_generated(xml)

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
                <p outputclass="title"><b>Procedure</b></p>
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

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/cmd[text()="Substep introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/info/codeblock[text()="Substep code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/info/p[text()="Substep explanation"])'))

    def test_alternating_substeps(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="title"><b>Procedure</b></p>
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

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(//steps/step/cmd[text()="Step introduction"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info/codeblock[text()="Step code"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[1]/p[text()="Step explanation"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[1]/substep/cmd[text()="First substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[1]/substep/stepxmp[text()="First substep example"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[2]/p[text()="Additional information"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[2]/substep/cmd[text()="Second substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/stepxmp[text()="Step example"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/info[3]/p[text()="Step summary"])'))

    def test_link_without_text(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li><xref href="http://example.com" format="html" scope="external" /></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/related-links/link[@href="http://example.com"])'))

    def test_link_with_text(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li><xref href="http://example.com" format="html" scope="external">Example link</xref></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/related-links/link[@href="http://example.com"])'))
        self.assertTrue(task.xpath('boolean(/task/related-links/link/linktext[text()="Example link"])'))

    def test_link_attributes(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Additional resources</b></p>
                <ul>
                    <li><xref href="http://example.com" format="html" scope="external" /></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(/task/related-links/link[@href="http://example.com"])'))
        self.assertTrue(task.xpath('boolean(/task/related-links/link[@format="html"])'))
        self.assertTrue(task.xpath('boolean(/task/related-links/link[@scope="external"])'))

    def test_universal_attributes(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="abstract" id="short-description" props="persona(sysadmin)" base="arch(x86_64)" platform="linux mac" product="dita-convert" audience="novice" otherprops="pdf" deliveryTarget="pdf" importance="normal" rev="v1.0.0" status="new" translate="yes" xml:lang="en-us" dir="ltr">Topic abstract</p>
                <p>Topic introduction</p>
                <p outputclass="title"><b>Procedure</b></p>
                <ol id="steps">
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
                <p outputclass="title"><b>Additional resources</b></p>
                <ul id="additional-resources">
                    <li><xref href="http://example.com" format="html" scope="external" id="external-link" /></li>
                </ul>
            </body>
        </topic>
        '''))

        task = transform.to_task_generated(xml)

        self.assertTrue(task.xpath('boolean(//shortdesc[@id="short-description"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@props="persona(sysadmin)"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@base="arch(x86_64)"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@platform="linux mac"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@product="dita-convert"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@audience="novice"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@otherprops="pdf"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@deliveryTarget="pdf"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@importance="normal"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@rev="v1.0.0"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@status="new"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@translate="yes"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@xml:lang="en-us"])'))
        self.assertTrue(task.xpath('boolean(//shortdesc[@dir="ltr"])'))
        self.assertFalse(task.xpath('boolean(//shortdesc/@outputclass)'))

        self.assertTrue(task.xpath('boolean(//steps[@id="steps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step[@id="first-step"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/cmd[@id="step-intro"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps[@id="substeps"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep[@id="first-substep"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/cmd[@id="substep-intro"])'))
        self.assertTrue(task.xpath('boolean(//steps/step/substeps/substep/stepxmp[@id="substep-example"])'))
        self.assertTrue(task.xpath('boolean(//related-links[@id="additional-resources"])'))
        self.assertTrue(task.xpath('boolean(//related-links/link[@id="external-link"])'))

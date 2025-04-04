import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToConcept(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <concept id="example-concept">
            <title>Concept title</title>
        </concept>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_concept_generated(xml)

        self.assertEqual(str(cm.exception), 'ERROR: Not a DITA topic')

    def test_nested_section(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <section>
                    <title>First section</title>
                    <section>
                        <title>Unsupported content</title>
                        <p>Unsupported content</p>
                    </section>
                </section>
                <section>
                    <title>Second section</title>
                </section>
            </body>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)
        err = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Nested sections not allowed in DITA, skipping...')

        self.assertFalse(concept.xpath('boolean(//section/section)'))
        self.assertFalse(concept.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/section[1]/title[text()="First section"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/section[2]/title[text()="Second section"])'))

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

        concept = transform.to_concept_generated(xml)
        err  = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Non-list elements found in related links, skipping...')

        self.assertFalse(concept.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))

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

        concept = transform.to_concept_generated(xml)
        err  = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Extra list elements found in related-links, skipping...')

        self.assertFalse(concept.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))

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

        concept = transform.to_concept_generated(xml)
        err  = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertIn('WARNING: No list elements found in related links', [m.message for m in err])

        self.assertFalse(concept.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))

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

        concept = transform.to_concept_generated(xml)
        err  = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertFalse(concept.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))

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

        concept = transform.to_concept_generated(xml)
        err  = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertFalse(concept.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))

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

        concept = transform.to_concept_generated(xml)
        err  = transform.to_concept_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))

    def test_concept_outputclass(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic" outputclass="concept">
            <title outputclass="main">Topic title</title>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)

        self.assertFalse(concept.xpath('boolean(/concept/@outputclass)'))
        self.assertTrue(concept.xpath('boolean(/concept[@id="example-topic"])'))
        self.assertTrue(concept.xpath('boolean(/concept/title[@outputclass="main"])'))

    def test_concept_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="abstract">Topic abstract</p>
                <p>Topic body</p>
            </body>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)

        self.assertEqual(concept.docinfo.xml_version, '1.0')
        self.assertEqual(concept.docinfo.public_id, '-//OASIS//DTD DITA Concept//EN')
        self.assertEqual(concept.docinfo.system_url, 'concept.dtd')

        self.assertTrue(concept.xpath('boolean(/concept)'))
        self.assertTrue(concept.xpath('boolean(/concept[@id="example-topic"])'))
        self.assertTrue(concept.xpath('boolean(/concept/title[text()="Topic title"])'))
        self.assertTrue(concept.xpath('boolean(/concept/shortdesc[text()="Topic abstract"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody)'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic body"])'))
        self.assertFalse(concept.xpath('boolean(/concept/conbody/p[text()="Topic abstract"])'))

    def test_multiple_abstracts(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="abstract">Topic abstract</p>
                <p outputclass="abstract">Topic introduction</p>
            </body>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/shortdesc[text()="Topic abstract"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[text()="Topic introduction"])'))
        self.assertFalse(concept.xpath('boolean(/concept/shortdesc[text()="Topic introduction"])'))
        self.assertFalse(concept.xpath('boolean(/concept/conbody/p[text()="Topic abstract"])'))

    def test_misplaced_abstract(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p>Topic introduction</p>
                <p outputclass="abstract">Topic abstract</p>
            </body>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[1][text()="Topic introduction"])'))
        self.assertTrue(concept.xpath('boolean(/concept/conbody/p[2][text()="Topic abstract"])'))
        self.assertFalse(concept.xpath('boolean(/concept/shortdesc)'))

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

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))
        self.assertFalse(concept.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(concept.xpath('boolean(//xref)'))

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

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link/linktext[text()="Example link"])'))
        self.assertFalse(concept.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(concept.xpath('boolean(//xref)'))

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

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@format="html"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@scope="external"])'))
        self.assertFalse(concept.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(concept.xpath('boolean(//xref)'))

    def test_link_in_section(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <section>
                    <title>Section title</title>
                    <p>Section introduction</p>
                    <p outputclass="title"><b>Additional resources</b></p>
                    <ul>
                        <li><xref href="http://example.com" format="html" scope="external">Example link</xref></li>
                    </ul>
                </section>
            </body>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link/linktext[text()="Example link"])'))
        self.assertFalse(concept.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(concept.xpath('boolean(//xref)'))

    def test_links_as_section(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p>Topic introduction</p>
                <section>
                    <title>Section title</title>
                    <p>Section introduction</p>
                </section>
                <section>
                    <title>Additional resources</title>
                    <ul>
                        <li><xref href="http://example.com" format="html" scope="external">Example link</xref></li>
                    </ul>
                </section>
            </body>
        </topic>
        '''))

        concept = transform.to_concept_generated(xml)

        self.assertTrue(concept.xpath('boolean(/concept/related-links/link[@href="http://example.com"])'))
        self.assertTrue(concept.xpath('boolean(/concept/related-links/link/linktext[text()="Example link"])'))
        self.assertTrue(concept.xpath('boolean(//section/title[text()="Section title"])'))
        self.assertTrue(concept.xpath('boolean(//section/p[text()="Section introduction"])'))
        self.assertFalse(concept.xpath('boolean(//section[title="Additional resources"])'))
        self.assertFalse(concept.xpath('boolean(//xref)'))

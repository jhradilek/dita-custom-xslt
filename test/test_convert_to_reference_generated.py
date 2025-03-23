import unittest
from io import StringIO
from lxml import etree
from src.dita.convert import transform

class TestDitaConvertToReference(unittest.TestCase):
    def test_document_is_topic(self):
        xml = etree.parse(StringIO('''\
        <reference id="example-reference">
            <title>Reference title</title>
        </reference>
        '''))

        with self.assertRaises(etree.XSLTApplyError) as cm:
            transform.to_reference_generated(xml)

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

        reference = transform.to_reference_generated(xml)
        err = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Nested sections not allowed in DITA, skipping...')

        self.assertFalse(reference.xpath('boolean(//section/section)'))
        self.assertFalse(reference.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section[2]/title[text()="First section"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section[3]/title[text()="Second section"])'))

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

        reference = transform.to_reference_generated(xml)
        err  = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Non-list elements found in related links, skipping...')

        self.assertFalse(reference.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))
        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@href="http://example.com"])'))

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

        reference = transform.to_reference_generated(xml)
        err  = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Extra list elements found in related-links, skipping...')

        self.assertFalse(reference.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))
        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@href="http://example.com"])'))

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

        reference = transform.to_reference_generated(xml)
        err  = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertIn('WARNING: No list elements found in related links', [m.message for m in err])

        self.assertFalse(reference.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))

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

        reference = transform.to_reference_generated(xml)
        err  = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertFalse(reference.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))

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

        reference = transform.to_reference_generated(xml)
        err  = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertFalse(reference.xpath('boolean(//*[text()="Unsupported content"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))

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

        reference = transform.to_reference_generated(xml)
        err  = transform.to_reference_generated.error_log

        self.assertIsNotNone(err.last_error)
        self.assertEqual(err.last_error.message, 'WARNING: Unexpected content found in related-links, skipping...')

        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))

    def test_reference_outputclass(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic" outputclass="reference">
            <title outputclass="main">Topic title</title>
        </topic>
        '''))

        reference = transform.to_reference_generated(xml)

        self.assertFalse(reference.xpath('boolean(/reference/@outputclass)'))
        self.assertTrue(reference.xpath('boolean(/reference[@id="example-topic"])'))
        self.assertTrue(reference.xpath('boolean(/reference/title[@outputclass="main"])'))

    def test_reference_structure(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <title>Topic title</title>
            <body>
                <p outputclass="abstract">Topic abstract</p>
                <p>Topic body</p>
            </body>
        </topic>
        '''))

        reference = transform.to_reference_generated(xml)

        self.assertEqual(reference.docinfo.xml_version, '1.0')
        self.assertEqual(reference.docinfo.public_id, '-//OASIS//DTD DITA Reference//EN')
        self.assertEqual(reference.docinfo.system_url, 'reference.dtd')

        self.assertTrue(reference.xpath('boolean(/reference)'))
        self.assertTrue(reference.xpath('boolean(/reference[@id="example-topic"])'))
        self.assertTrue(reference.xpath('boolean(/reference/title[text()="Topic title"])'))
        self.assertTrue(reference.xpath('boolean(/reference/shortdesc[text()="Topic abstract"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody)'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section)'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic body"])'))
        self.assertFalse(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic abstract"])'))

    def test_multiple_abstracts(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p outputclass="abstract">Topic abstract</p>
                <p outputclass="abstract">Topic introduction</p>
            </body>
        </topic>
        '''))

        reference = transform.to_reference_generated(xml)

        self.assertTrue(reference.xpath('boolean(/reference/shortdesc[text()="Topic abstract"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic introduction"])'))
        self.assertFalse(reference.xpath('boolean(/reference/shortdesc[text()="Topic introduction"])'))
        self.assertFalse(reference.xpath('boolean(/reference/refbody/section/p[text()="Topic abstract"])'))

    def test_misplaced_abstract(self):
        xml = etree.parse(StringIO('''\
        <topic id="example-topic">
            <body>
                <p>Topic introduction</p>
                <p outputclass="abstract">Topic abstract</p>
            </body>
        </topic>
        '''))

        reference = transform.to_reference_generated(xml)

        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[1][text()="Topic introduction"])'))
        self.assertTrue(reference.xpath('boolean(/reference/refbody/section/p[2][text()="Topic abstract"])'))
        self.assertFalse(reference.xpath('boolean(/reference/shortdesc)'))

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

        reference = transform.to_reference_generated(xml)

        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@href="http://example.com"])'))
        self.assertFalse(reference.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(reference.xpath('boolean(//xref)'))

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

        reference = transform.to_reference_generated(xml)

        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@href="http://example.com"])'))
        self.assertTrue(reference.xpath('boolean(/reference/related-links/link/linktext[text()="Example link"])'))
        self.assertFalse(reference.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(reference.xpath('boolean(//xref)'))

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

        reference = transform.to_reference_generated(xml)

        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@href="http://example.com"])'))
        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@format="html"])'))
        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@scope="external"])'))
        self.assertFalse(reference.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(reference.xpath('boolean(//xref)'))

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

        reference = transform.to_reference_generated(xml)

        self.assertTrue(reference.xpath('boolean(/reference/related-links/link[@href="http://example.com"])'))
        self.assertTrue(reference.xpath('boolean(/reference/related-links/link/linktext[text()="Example link"])'))
        self.assertFalse(reference.xpath('boolean(//p[@outputclass="title"])'))
        self.assertFalse(reference.xpath('boolean(//xref)'))

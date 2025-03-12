import unittest
import contextlib
import errno
from io import StringIO
from lxml import etree
from unittest.mock import mock_open, patch
from src.dita.convert import cli
from src.dita.convert import NAME, VERSION

class TestDitaCli(unittest.TestCase):
    def test_invalid_option(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stderr(StringIO()) as err:
            cli.parse_args(['--invalid'])

        self.assertEqual(cm.exception.code, errno.ENOENT)
        self.assertRegex(err.getvalue(), rf'^usage: {NAME}')

    def test_opt_help_short(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stdout(StringIO()) as out:
            cli.parse_args(['-h'])

        self.assertEqual(cm.exception.code, 0)
        self.assertRegex(out.getvalue(), rf'^usage: {NAME}')

    def test_opt_help_long(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stdout(StringIO()) as out:
            cli.parse_args(['--help'])

        self.assertEqual(cm.exception.code, 0)
        self.assertRegex(out.getvalue(), rf'^usage: {NAME}')

    def test_opt_version_short(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stdout(StringIO()) as out:
            cli.parse_args(['-v'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), f'{NAME} {VERSION}')

    def test_opt_version_long(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stdout(StringIO()) as out:
            cli.parse_args(['--version'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), f'{NAME} {VERSION}')

    def test_opt_type_invalid(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stderr(StringIO()) as err:
                cli.parse_args(['--type', 'topic', 'topic.dita'])

        self.assertEqual(cm.exception.code, errno.ENOENT)
        self.assertRegex(err.getvalue(), rf'^usage: {NAME}')

    def test_opt_type_long(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                cli.parse_args(['--type', 'concept', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')

    def test_opt_type_concept(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                cli.parse_args(['-t', 'concept', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')

    def test_opt_type_task(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<task />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                cli.parse_args(['-t', 'task', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<task />')

    def test_opt_type_reference(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<reference />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                cli.parse_args(['-t', 'reference', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<reference />')

    def test_opt_output_short(self):
        with patch('src.dita.convert.cli.convert') as convert,\
             patch('src.dita.convert.cli.open') as file_open:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                    cli.parse_args(['-t', 'concept', '-o', 'out.dita', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '')
        file_open.assert_called_once_with('out.dita', 'w')
        file_open().__enter__().write.assert_called_once_with('<concept />')

    def test_opt_output_long(self):
        with patch('src.dita.convert.cli.convert') as convert,\
             patch('src.dita.convert.cli.open') as file_open:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                    cli.parse_args(['-t', 'concept', '--output', 'out.dita', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '')
        file_open.assert_called_once_with('out.dita', 'w')
        file_open().__enter__().write.assert_called_once_with('<concept />')

    def test_opt_output_stdout(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                    cli.parse_args(['-t', 'concept', '-o', '-', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')

    def test_opt_generated_short(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                     cli.parse_args(['-t', 'concept', '-g', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')
        convert.assert_called_once_with('topic.dita', 'concept', True)

    def test_opt_generated_long(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                     cli.parse_args(['-t', 'concept', '--generated', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')
        convert.assert_called_once_with('topic.dita', 'concept', True)

    def test_opt_no_generated_short(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                     cli.parse_args(['-t', 'concept', '-G', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')
        convert.assert_called_once_with('topic.dita', 'concept', False)

    def test_opt_no_generated_short(self):
        with patch('src.dita.convert.cli.convert') as convert:
            convert.return_value = '<concept />'

            with self.assertRaises(SystemExit) as cm,\
                 contextlib.redirect_stdout(StringIO()) as out:
                     cli.parse_args(['-t', 'concept', '--no-generated', 'topic.dita'])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(out.getvalue().rstrip(), '<concept />')
        convert.assert_called_once_with('topic.dita', 'concept', False)

    def test_invalid_file(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stderr(StringIO()) as err:
                 cli.parse_args(['-t', 'concept', 'topic.dita'])

        self.assertEqual(cm.exception.code, errno.ENOENT)
        self.assertRegex(err.getvalue(), rf'^{NAME}:.*topic\.dita')

    def test_get_type_concept(self):
        xml = etree.parse(StringIO('<topic outputclass="concept" />'))

        with contextlib.redirect_stderr(StringIO()) as err:
            target_type = cli.get_type('topic.dita', xml)

        self.assertEqual(err.getvalue().rstrip(), '')
        self.assertEqual(target_type, 'concept')

    def test_get_type_procedure(self):
        xml = etree.parse(StringIO('<topic outputclass="procedure" />'))

        with contextlib.redirect_stderr(StringIO()) as err:
            target_type = cli.get_type('topic.dita', xml)

        self.assertEqual(err.getvalue().rstrip(), '')
        self.assertEqual(target_type, 'task')

    def test_get_type_task(self):
        xml = etree.parse(StringIO('<topic outputclass="task" />'))

        with contextlib.redirect_stderr(StringIO()) as err:
            target_type = cli.get_type('topic.dita', xml)

        self.assertEqual(err.getvalue().rstrip(), '')
        self.assertEqual(target_type, 'task')

    def test_get_type_reference(self):
        xml = etree.parse(StringIO('<topic outputclass="reference" />'))

        with contextlib.redirect_stderr(StringIO()) as err:
            target_type = cli.get_type('topic.dita', xml)

        self.assertEqual(err.getvalue().rstrip(), '')
        self.assertEqual(target_type, 'reference')

    def test_get_type_missing(self):
        xml = etree.parse(StringIO('<topic />'))

        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stderr(StringIO()) as err:
            target_type = cli.get_type('topic.dita', xml)

        self.assertEqual(cm.exception.code, errno.EINVAL)
        self.assertRegex(err.getvalue(), r'topic\.dita: error: outputclass not found')

    def test_get_type_invalid(self):
        xml = etree.parse(StringIO('<topic outputclass="snippet" />'))

        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stderr(StringIO()) as err:
            target_type = cli.get_type('topic.dita', xml)

        self.assertEqual(cm.exception.code, errno.EINVAL)
        self.assertRegex(err.getvalue(), r'topic\.dita: error: unsupported outputclass "snippet"')

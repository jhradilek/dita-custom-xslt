import unittest
import contextlib
import errno
from io import StringIO
from unittest.mock import mock_open, patch
from src.dita.convert import cli
from src.dita.convert import NAME, VERSION

class TestDitaCli(unittest.TestCase):
    def test_no_options(self):
        with self.assertRaises(SystemExit) as cm,\
             contextlib.redirect_stderr(StringIO()) as err:
            cli.parse_args([])

        self.assertEqual(cm.exception.code, errno.ENOENT)
        self.assertRegex(err.getvalue(), rf'^usage: {NAME}')

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

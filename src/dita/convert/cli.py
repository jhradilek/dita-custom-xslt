# Copyright (C) 2024, 2025 Jaromir Hradilek

# MIT License
#
# Permission  is hereby granted,  free of charge,  to any person  obtaining
# a copy of  this software  and associated documentation files  (the "Soft-
# ware"),  to deal in the Software  without restriction,  including without
# limitation the rights to use,  copy, modify, merge,  publish, distribute,
# sublicense, and/or sell copies of the Software,  and to permit persons to
# whom the Software is furnished to do so,  subject to the following condi-
# tions:
#
# The above copyright notice  and this permission notice  shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS",  WITHOUT WARRANTY OF ANY KIND,  EXPRESS
# OR IMPLIED,  INCLUDING BUT NOT LIMITED TO  THE WARRANTIES OF MERCHANTABI-
# LITY,  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS  BE LIABLE FOR ANY CLAIM,  DAMAGES
# OR OTHER LIABILITY,  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM,  OUT OF OR IN CONNECTION WITH  THE SOFTWARE  OR  THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import argparse
import errno
import sys

from lxml import etree
from . import NAME, VERSION, DESCRIPTION
from .transform import to_concept, to_reference, to_task, \
                       to_concept_generated, to_reference_generated, \
                       to_task_generated

# Print a message to standard error output and terminate the script:
def exit_with_error(error_message: str, exit_status: int = errno.EPERM) -> None:
    # Print the supplied message to standard error output:
    print(f'{NAME}: {error_message}', file=sys.stderr)

    # Terminate the script with the supplied exit status:
    sys.exit(exit_status)

# Extract the content type from the root element outputclass:
def get_type(source_file: str, source_xml: etree._ElementTree) -> str:
    # Get the root element attributes:
    attributes = source_xml.getroot().attrib

    # Verify that the outputclass attribute is defined:
    if 'outputclass' not in attributes:
        exit_with_error(f'{source_file}: error: outputclass not found, use -t/--type', errno.EINVAL)

    # Get the outputclass attribute value:
    output_class = str(attributes['outputclass'].lower())

    # Verify that the outputclass value is supported:
    if output_class not in ['assembly', 'concept', 'procedure', 'task', 'reference']:
        exit_with_error(f'{source_file}: error: unsupported outputclass "{output_class}", use -t/--type', errno.EINVAL)

    # Adjust the outputclass if needed:
    if output_class == 'assembly':
        output_class = output_class.replace('assembly', 'concept')
    if output_class == 'procedure':
        output_class = output_class.replace('procedure', 'task')

    # Return the adjusted outputclass:
    return output_class

# Convert the selected file:
def convert(source_file: str, target_type: str | None = None, generated: bool = False) -> str:
    # Parse the source file:
    try:
        source_xml = etree.parse(source_file)
    except etree.XMLSyntaxError as message:
        exit_with_error(f'{source_file}: error: {message}')

    # Determine the target type from the source file if not provided:
    if target_type is None:
        target_type = get_type(source_file, source_xml)

    # Select the appropriate XSLT transformer:
    transform = {
        False: {
            'concept':       to_concept,
            'reference':     to_reference,
            'task':          to_task,
        },
        True: {
            'concept':   to_concept_generated,
            'reference': to_reference_generated,
            'task':      to_task_generated,
        },
    }[generated][target_type]

    # Run the transformation:
    try:
        xml = transform(source_xml)
    except etree.XSLTApplyError as message:
        exit_with_error(f'{source_file}: {message}')

    # Print any warning messages to standard error output:
    if hasattr(transform, 'error_log'):
        for error in transform.error_log:
            print(f'{source_file}: {error.message}', file=sys.stderr)

    # Return the result:
    return str(xml)

# Parse supplied command-line options:
def parse_args(argv: list[str] | None = None) -> None:
    # Configure the option parser:
    parser = argparse.ArgumentParser(prog=NAME,
        description=DESCRIPTION,
        add_help=False)

    # Redefine section titles for the main command:
    parser._optionals.title = 'Options'
    parser._positionals.title = 'Arguments'

    # Add supported command-line options:
    info = parser.add_mutually_exclusive_group()
    gen  = parser.add_mutually_exclusive_group()
    parser.add_argument('-o', '--output',
        default=sys.stdout,
        help='write output to the selected file instead of stdout')
    parser.add_argument('-t', '--type',
        choices=('concept', 'reference', 'task'),
        default=None,
        help='specify the target DITA content type')
    gen.add_argument('-g', '--generated',
        default=False,
        action='store_true',
        help='specify that the input file is generated by asciidoctor-dita-topic')
    gen.add_argument('-G', '--no-generated',
        dest='generated',
        action='store_false',
        help='specify that the input file is a generic DITA topic (default)')
    info.add_argument('-h', '--help',
        action='help',
        help='display this help and exit')
    info.add_argument('-v', '--version',
        action='version',
        version=f'{NAME} {VERSION}',
        help='display version information and exit')

    # Add supported command-line arguments:
    parser.add_argument('file', metavar='FILE',
        default=sys.stdin,
        nargs='?',
        help='specify the DITA topic file to convert')

    # Parse the command-line options:
    args = parser.parse_args(argv)

    # Recognize the instruction to read from standard input:
    if args.file == '-':
        args.file = sys.stdin

    # Convert the selected file:
    try:
        xml = convert(args.file, args.type, args.generated)
    except OSError as message:
        exit_with_error(str(message), errno.ENOENT)

    # Determine whether to write to standard output:
    if args.output == sys.stdout or args.output == '-':
        # Print to standard output:
        sys.stdout.write(xml)

        # Terminate the script:
        sys.exit(0)

    # Write to the selected file:
    try:
        with open(args.output, 'w') as f:
            f.write(xml)
    except Exception as ex:
        exit_with_error(f'{args.output}: {ex}')

    # Return success:
    sys.exit(0)

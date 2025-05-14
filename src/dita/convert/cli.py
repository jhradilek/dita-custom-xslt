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
import os

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

# Print a message to standard error output:
def warn(error_message: str) -> None:
    # Print the supplied message to standard error output:
    print(f'{NAME}: {error_message}', file=sys.stderr)

# Extract the content type from the root element outputclass:
def get_type(source_file: str, source_xml: etree._ElementTree) -> str:
    # Get the root element attributes:
    attributes = source_xml.getroot().attrib

    # Verify that the outputclass attribute is defined:
    if 'outputclass' not in attributes:
        raise Exception(f'{source_file}: error: outputclass not found, use -t/--type')

    # Get the outputclass attribute value:
    output_class = str(attributes['outputclass'].lower())

    # Verify that the outputclass value is supported:
    if output_class not in ['assembly', 'concept', 'procedure', 'task', 'reference']:
        raise Exception(f'{source_file}: error: unsupported outputclass "{output_class}", use -t/--type')

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
        raise Exception(f'{source_file}: error: {message}')

    # Determine the target type from the source file if not provided:
    if target_type is None:
        try:
            target_type = get_type(source_file, source_xml)
        except Exception as message:
            raise Exception(message)

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
        raise Exception(f'{source_file}: {message}')

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
    out  = parser.add_mutually_exclusive_group()
    out.add_argument('-o', '--output', metavar='FILE',
        default=sys.stdout,
        help='write output to the selected file instead of stdout')
    out.add_argument('-d', '--directory', metavar='DIRECTORY',
        default=False,
        help='write output to the selected directory instead of stdout')
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
    parser.add_argument('files', metavar='FILE',
        default='-',
        nargs='*',
        help='specify the DITA topic files to convert')

    # Parse the command-line options:
    args = parser.parse_args(argv)

    # Set the initial exit code:
    exit_code = 0

    # Recognize the instruction to read from standard input:
    if args.files == '-':
        args.files = [sys.stdin]

    # Recognize the instruction to write to standard output:
    if args.output == '-':
        args.output = sys.stdout

    # Create the target directory:
    if args.directory:
        try:
            os.makedirs(args.directory)
        except FileExistsError:
            pass
        except Exception:
            exit_with_error(f'error: Unable to create target directory: {args.directory}', errno.EACCES)

    # Process all supplied files:
    for input_file in args.files:
        try:
            # Convert the selected file:
            xml = convert(input_file, args.type, args.generated)
        except (OSError, Exception) as message:
            # Report the error:
            warn(str(message))

            # Update the exit code:
            exit_code = errno.EPERM

            # Do not proceed further with this file:
            continue

        # Determine whether to write to standard output:
        if args.output == sys.stdout and not args.directory:
            # Print the converted content to standard output:
            sys.stdout.write(xml)

            # Proceed to the next file:
            continue

        # Compose the target file path:
        if args.directory:
            if input_file == sys.stdin:
                output_file = str(os.path.join(args.directory, 'out.adoc'))
            else:
                output_file = str(os.path.join(args.directory, os.path.basename(input_file)))
        else:
            output_file = args.output

        try:
            # Write the converted content to the selected file:
            with open(output_file, 'w') as f:
                f.write(xml)
        except Exception as ex:
            # Report the error:
            warn(f'{output_file}: {ex}')

            # Update the exit code:
            exit_code = errno.EPERM

    # Return the exit code:
    sys.exit(exit_code)

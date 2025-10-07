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

from copy import deepcopy
from lxml import etree
from uuid import uuid4
from . import NAME, VERSION, DESCRIPTION
from .transform import to_concept, to_reference, to_task, \
                       to_concept_generated, to_reference_generated, \
                       to_task_generated, to_single_topic, to_single_map

# Define which symbols are to be exported:
__all__ = ['convert', 'run']

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

# Ensure that the XML element has a valid ID attribute set:
def fix_element_id(xml_element: etree._Element) -> None:
    # Check if the XML element already has an ID set:
    if xml_element.attrib and xml_element.attrib.has_key('id'):
        return

    # Generate a unique ID:
    xml_element.set('id', str(uuid4()))

# Ensure that the XML element has a valid outputclass:
def fix_element_outputclass(xml_element: etree._Element) -> None:
    # Check if the XML element already has a valid output class:
    if xml_element.attrib and xml_element.attrib.has_key('outputclass'):
        outputclass = xml_element.attrib['outputclass']

        # Check if the outputclass has a supported value:
        if outputclass in ['concept', 'reference', 'procedure']:
            return

        # Use the parent outputclass instead of snippets:
        if outputclass == 'snippet':
            parent = xml_element.getparent()
            if parent is not None:
                xml_element.set('outputclass', str(parent.attrib['outputclass']))
                return

    # Use concept by default:
    xml_element.set('outputclass', 'concept')

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
def convert(source_file: str, source_xml: etree._ElementTree, target_type: str | None = None, generated: bool = False) -> etree._XSLTResultTree:
    # Determine the target type from the source file if not provided:
    if target_type is None:
        target_type = get_type(source_file, source_xml)

    # Select the appropriate XSLT transformer:
    transform = {
        False: {
            'concept':       to_concept,
            'reference':     to_reference,
            'task':          to_task,
            'single_topic':  to_single_topic,
            'single_map':    to_single_map,
        },
        True: {
            'concept':   to_concept_generated,
            'reference': to_reference_generated,
            'task':      to_task_generated,
            'single_topic':  to_single_topic,
            'single_map':    to_single_map,
        },
    }[generated][target_type]

    # Run the transformation:
    xml = transform(source_xml)

    # Print any warning messages to standard error output:
    if hasattr(transform, 'error_log'):
        for error in transform.error_log:
            print(f'{source_file}: {error.message}', file=sys.stderr)

    # Return the result:
    return xml

# Convert individual topics:
def convert_topics(args: argparse.Namespace) -> int:
    # Set the initial exit code:
    exit_code = 0

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
            # Parse the source file:
            input_xml = etree.parse(input_file)

            # Convert the selected file:
            xml = convert(input_file, input_xml, args.type, args.generated)
        except (etree.XMLSyntaxError, etree.XSLTApplyError) as message:
            # Report the error:
            warn(f'{input_file}: error: {message}')

            # Do not proceed further with this file:
            exit_code = errno.EPERM
            continue
        except (OSError, Exception) as message:
            # Report the error:
            warn(str(message))

            # Do not proceed further with this file:
            exit_code = errno.EPERM
            continue

        # Determine whether to write to standard output:
        if args.output == sys.stdout and not args.directory:
            # Print the converted content to standard output:
            sys.stdout.write(str(xml))

            # Proceed to the next file:
            continue

        # Compose the target file path:
        if args.directory:
            if input_file == sys.stdin:
                output_file = str(os.path.join(args.directory, 'out.dita'))
            else:
                output_file = str(os.path.join(args.directory, os.path.basename(input_file)))
        else:
            output_file = args.output

        try:
            # Write the converted content to the selected file:
            with open(output_file, 'w') as f:
                f.write(str(xml))
        except Exception as message:
            # Report the error:
            warn(f'{output_file}: {message}')

            # Update the exit code:
            exit_code = errno.EPERM

    # Return the exit code:
    return exit_code

# Split supplied topics:
def split_topics(args: argparse.Namespace) -> int:
    # Set the initial exit code:
    exit_code = 0

    # Create the target directory:
    try:
        os.makedirs(args.directory)
    except FileExistsError:
        pass
    except Exception:
        exit_with_error(f'error: Unable to create target directory: {args.directory}', errno.EACCES)

    # Process all supplied files:
    for input_file in args.files:
        try:
            # Parse the supplied file:
            input_xml = etree.parse(input_file)

            # Convert the supplied file to a topic with nested topics:
            xml = convert(input_file, input_xml, 'single_topic', args.generated)
        except (etree.XMLSyntaxError, etree.XSLTApplyError) as message:
            # Report the error:
            warn(f'{input_file}: error: {message}')

            # Do not proceed further with this file:
            exit_code = errno.EPERM
            continue
        except (OSError, Exception) as message:
            # Report the error:
            warn(str(message))

            # Do not proceed further with this file:
            exit_code = errno.EPERM
            continue

        # Process each topic individually:
        for element in xml.iter():
            # Skip elements other than topics:
            if element.tag != 'topic':
                continue

            # Ensure that the topic has a valid ID:
            fix_element_id(element)

            # Ensure that the topic has a valid outputclass:
            fix_element_outputclass(element)

            # Create a copy of the topic subtree:
            topic = etree.ElementTree(deepcopy(element))

            # Remove all nested topics:
            for e in topic.findall('.//topic'):
                parent = e.getparent()
                if parent is not None:
                    parent.remove(e)

            try:
                # Convert the selected file in nested topics:
                out = convert(input_file, topic, None, args.generated)
            except etree.XSLTApplyError as message:
                # Report the error:
                warn(f'{input_file}: error: {message}')

                # Do not proceed further with this file:
                exit_code = errno.EPERM
                continue

            # Compose the target file path:
            output_file = str(os.path.join(args.directory, str(element.attrib["id"]) + '.dita'))

            try:
                # Write the converted content to the selected file:
                with open(output_file, 'w') as f:
                    f.write(str(out))
            except Exception as message:
                # Report the error:
                warn(f'{output_file}: {message}')

                # Update the exit code:
                exit_code = errno.EPERM

        # Generate the DITA map:
        try:
            # Convert the supplied file to a DITA map:
            out = convert(input_file, xml, 'single_map', args.generated)
        except etree.XSLTApplyError as message:
            # Report the error:
            warn(f'{input_file}: error: {message}')

            # Do not proceed further with this file:
            exit_code = errno.EPERM
            continue

        # Compose the target file path:
        output_file = str(os.path.join(args.directory, str(xml.getroot().attrib["id"]) + '.ditamap'))

        try:
            # Write the converted DITA map to the selected file:
            with open(output_file, 'w') as f:
                f.write(str(out))
        except Exception as message:
            # Report the error:
            warn(f'{output_file}: {message}')

            # Update the exit code:
            exit_code = errno.EPERM

    # Return the exit code:
    return exit_code

# Parse supplied command-line options:
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    # Configure the option parser:
    parser = argparse.ArgumentParser(prog=NAME,
        description=DESCRIPTION,
        add_help=False)

    # Redefine section titles for the main command:
    parser._optionals.title = 'Options'
    parser._positionals.title = 'Arguments'

    # Add supported command-line options:
    info = parser.add_mutually_exclusive_group()
    act  = parser.add_mutually_exclusive_group()
    gen  = parser.add_mutually_exclusive_group()
    out  = parser.add_mutually_exclusive_group()
    act.add_argument('-s', '--split-topic',
        default=False,
        action='store_true',
        help='specify that the input file sould be split to individual ' +
             'topics; this option is mutually exclusive with -t and ' +
             'requires -d to be specified')
    act.add_argument('-t', '--type',
        choices=('concept', 'reference', 'task'),
        default=None,
        help='specify the target DITA content type when converting ' +
             'individual topics; this option is mutually exclusive with ' +
             '-s')
    gen.add_argument('-g', '--generated',
        default=False,
        action='store_true',
        help='specify that the input file is generated by the ' +
             'dita-topic plugin; this option is mutually exclusive with -G')
    gen.add_argument('-G', '--no-generated',
        dest='generated',
        action='store_false',
        help='specify that the input file is a generic DITA topic ' +
             '(default); this option is mutually exclusive with -g')
    out.add_argument('-o', '--output', metavar='FILE',
        default=sys.stdout,
        help='write output to the selected file instead of stdout; this ' +
             'option is mutually exclusive with -d')
    out.add_argument('-d', '--directory', metavar='DIRECTORY',
        default=False,
        help='write output to the selected directory instead of stdout; ' +
             'this option is mutually exclusive with -o')
    info.add_argument('-h', '--help',
        action='help',
        help='display this help and exit')
    info.add_argument('-v', '--version',
        action='version',
        version=f'{NAME} {VERSION}',
        help='display version information and exit')

    # Add supported command-line arguments:
    parser.add_argument('files', metavar='FILE',
        default=['-'],
        nargs='*',
        help='specify one or more DITA topics to convert')

    # Parse the command-line options:
    args = parser.parse_args(argv)

    # Verify required and unsupported option combinations:
    if args.split_topic and not args.directory:
        parser.print_usage(file=sys.stderr)
        exit_with_error('the -s option requires -d to be specified', errno.ENOENT)

    # Recognize the instruction to read from standard input:
    if args.files == ['-']:
        args.files = [sys.stdin]

    # Recognize the instruction to write to standard output:
    if args.output == '-':
        args.output = sys.stdout

    # Return the parsed arguments:
    return args

# The main entry point:
def run(argv: list[str] | None = None) -> None:
    try:
        # Parse command-line option:
        args = parse_args(argv)

        # Determine the correct action:
        if args.split_topic:
            exit_code = split_topics(args)
        else:
            exit_code = convert_topics(args)
    except KeyboardInterrupt:
        sys.exit(130)

    # Terminate the script:
    sys.exit(exit_code)

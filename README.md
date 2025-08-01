# DITA Custom XSLT

**dita-custom-xslt** is a set of XSLT stylesheets that convert a generic DITA topic to a specialized DITA concept, reference, or task. **dita-convert** is a Python 3 package that provides a convenient access to these stylesheets and a command-line utility to perform the conversions.

In combination with [asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale) and [asciidoctor-dita-topic](https://github.com/jhradilek/asciidoctor-dita-topic), this project can be used to rapidly convert AsciiDoc content to DITA:

1.  Identify incompatible markup in the AsciiDoc source file:

    ```console
    $ vale source_file.adoc
    ```
2.  Convert the AsciiDoc file to a generic DITA topic:

    ```console
    $ asciidoctor -r dita-topic -b dita-topic source_file.adoc
    ```
3.  Convert the generic DITA topic to a specialized DITA concept, reference, or task:

    ```console
    $ dita-convert -gt task source_file.dita
    ```

## Installation

Install the `dita-convert` Python package:

```
python3 -m pip install --upgrade dita-convert
```

## Usage

### Using the command-line interface

To convert a DITA topic to a specialized DITA content type, run the following command:

```
python3 -m dita.convert -t TYPE TOPIC_FILE
```

For convenience, the package provides a wrapper script that you can run directly as follows:

```
dita-convert -t TYPE TOPIC_FILE
```

Available `TYPE` values are `concept`, `reference`, or `task`.

By default, the script treats the source file as a generic DITA topic. To convert files generated by [asciidoctor-dita-topic](https://github.com/jhradilek/asciidoctor-dita-topic) that follow the guidelines for modules as defined in the [Modular Documentation Reference Guide](https://redhat-documentation.github.io/modular-docs/), add the `-g` option:

```
dita-convert -t TYPE -g TOPIC_FILE
```

For generated topics, this is the preferred method because `asciidoctor-dita-topic` includes predictable headings that allow parts of the document to be correctly identified as `prereq`, `result`, `tasktroubleshooting`, `postreq`, and `related-links`. If the original AsciiDoc files included valid content type definitions, you can also omit the `-t` option.

For a complete list of available command-line options, run `dita-convert` with the `-h` option:

```
dita-convert -h
```

### Using the Python interface 

To convert a DITA topic to a specialized DITA content type, the **dita-convert** package exports the corresponding `to_concept()`, `to_reference()`, `to_task()`, `to_concept_generated()`, `to_reference_generated()`, and `to_task_generated()` functions that return an `ElementTree` object:

```python
import sys

from lxml import etree
from dita.convert import to_task

# Parse the contents of a sample DITA topic file:
topic = etree.parse("topic.dita")

# Report possible errors:
try:
    # Convert the DITA topic to a DITA task:
    task  = to_task(topic)
except etree.XSLTApplyError as msg:
    # Print the error message to standard error output:
    print(msg, file=sys.stderr)

    # Terminate the script:
    sys.exit(1)

# Report possible warnings:
for error in to_task.error_log:
    # Print the warning message to standard error output:
    print(error.message, file=sys.stderr)

# Print the resulting XML to standard output:
print(str(task))
```

If you prefer to work with the underlying XSLT stylesheets directly, you can access their Path objects as follows:

```python
from dita.convert import xslt

# Print the full path to the XSLT stylesheet for DITA reference:
print(xslt.reference)
```

Available variables are `concept`, `reference`, `task`, `concept_generated`, `reference_generated`, and `task_generated`.

## Copyright

Copyright © 2024, 2025 Jaromir Hradilek

This program is free software, released under the terms of the MIT license. It is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

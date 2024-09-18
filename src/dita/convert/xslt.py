# Copyright (C) 2024 Jaromir Hradilek

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

from pathlib import Path
from lxml import etree

# XSLT file paths:
concept_path        = Path(__file__).parent / 'xslt/concept.xsl'
reference_path      = Path(__file__).parent / 'xslt/reference.xsl'
task_path           = Path(__file__).parent / 'xslt/task.xsl'
task_generated_path = Path(__file__).parent / 'xslt/task-generated.xsl'

# XSTL transformers:
to_concept          = etree.XSLT(etree.parse(concept_path))
to_reference        = etree.XSLT(etree.parse(reference_path))
to_task             = etree.XSLT(etree.parse(task_path))
to_task_generated   = etree.XSLT(etree.parse(task_generated_path))

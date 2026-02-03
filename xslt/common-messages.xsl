<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2026 Jaromir Hradilek

  A collection of  XSLT matches  used by other stylesheets to report common
  errors and warnings.

  MIT License

  Permission  is hereby granted,  free of charge,  to any person  obtaining
  a copy of  this software  and associated documentation files  (the "Soft-
  ware"),  to deal in the Software  without restriction,  including without
  limitation the rights to use,  copy, modify, merge,  publish, distribute,
  sublicense, and/or sell copies of the Software,  and to permit persons to
  whom the Software is furnished to do so,  subject to the following condi-
  tions:

  The above copyright notice  and this permission notice  shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS",  WITHOUT WARRANTY OF ANY KIND,  EXPRESS
  OR IMPLIED,  INCLUDING BUT NOT LIMITED TO  THE WARRANTIES OF MERCHANTABI-
  LITY,  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT
  SHALL THE AUTHORS OR COPYRIGHT HOLDERS  BE LIABLE FOR ANY CLAIM,  DAMAGES
  OR OTHER LIABILITY,  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
  ARISING FROM,  OUT OF OR IN CONNECTION WITH  THE SOFTWARE  OR  THE USE OR
  OTHER DEALINGS IN THE SOFTWARE.
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <!-- Report an error if the converted file is not a DITA topic: -->
  <xsl:template match="/*[not(self::topic)]">
    <xsl:message terminate="yes">ERROR: Not a DITA topic</xsl:message>
  </xsl:template>

  <!-- Report an error if the converted file contains an incomplete definition list: -->
  <xsl:template match="//dt[not(following-sibling::dd)]">
    <xsl:message terminate="yes">ERROR: Incomplete definition list</xsl:message>
  </xsl:template>

</xsl:stylesheet>

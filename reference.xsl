<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2024 Jaromir Hradilek

  A custom XSLT stylesheet  to convert a generic DITA topic  generated with
  the  asciidoctor-dita-topic[1]  plug-in  to a specialized DITA reference.
  The stylesheet expects  that the original AsciiDoc file  has followed the
  guidelines  for concept modules  as defined  in the Modular Documentation
  Reference Guide[2].

  Usage: xsltproc ––novalid reference.xsl YOUR_TOPIC.dita

  [1] https://github.com/jhradilek/asciidoctor-dita-topic
  [2] https://redhat-documentation.github.io/modular-docs/

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
  <!-- Generate the XML and DOCTYPE declarations: -->
  <xsl:output encoding="utf-8" method="xml" doctype-system="reference.dtd" doctype-public="-//OASIS//DTD DITA Reference//EN" />

  <!-- Format the XML output: -->
  <xsl:output indent="yes" />
  <xsl:strip-space elements="*" />

  <!-- Perform identity transformation: -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <!-- Generate reference as the root element: -->
  <xsl:template match="/topic">
    <xsl:element name="reference">
      <xsl:apply-templates select="@*|node()" />
    </xsl:element>
  </xsl:template>

  <!-- Generate the conbody element: -->
  <xsl:template match="body">
    <xsl:element name="refbody">
      <xsl:choose>
        <xsl:when test="section">
          <xsl:element name="section">
            <xsl:apply-templates select="section[1]/preceding-sibling::*" />
          </xsl:element>
          <xsl:apply-templates select="section[1]/following-sibling::*" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:element name="section">
            <xsl:apply-templates select="@*|node()" />
          </xsl:element>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>

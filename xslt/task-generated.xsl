<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2024 Jaromir Hradilek

  A custom XSLT stylesheet  to convert a generic DITA topic  generated with
  the  asciidoctor-dita-topic[1] plug-in  to a specialized DITA task topic.
  The stylesheet expects  that the original AsciiDoc file  has followed the
  guidelines for procedure modules as defined  in the Modular Documentation
  Reference Guide[2].

  Usage: xsltproc ––novalid task-generated.xsl YOUR_TOPIC.dita

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
  <!-- Compose the XML and DOCTYPE declarations: -->
  <xsl:output encoding="utf-8" method="xml" doctype-system="task.dtd" doctype-public="-//OASIS//DTD DITA Task//EN" />

  <!-- Format the XML output: -->
  <xsl:output indent="yes" />
  <xsl:strip-space elements="*" />

  <!-- Report an error if the converted file is not a DITA topic: -->
  <xsl:template match="/*[not(self::topic)]">
    <xsl:message terminate="yes">ERROR: Not a DITA topic</xsl:message>
  </xsl:template>

  <!-- Report an error if the converted file contains a section: -->
  <xsl:template match="//section">
    <xsl:message terminate="yes">ERROR: Section not allowed in a DITA task</xsl:message>
  </xsl:template>

  <!-- Perform identity transformation: -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <!-- Generate task as the root element: -->
  <xsl:template match="/topic">
    <xsl:element name="task">
      <xsl:apply-templates select="@*|node()" />
    </xsl:element>
  </xsl:template>

  <!-- Generate the taskbody element: -->
  <xsl:template match="body">
    <xsl:element name="taskbody">
      <xsl:call-template name="prereq" />
      <xsl:call-template name="context" />
      <xsl:call-template name="steps" />
      <xsl:call-template name="result" />
      <xsl:call-template name="tasktroubleshooting" />
      <xsl:call-template name="postreq" />
    </xsl:element>
  </xsl:template>

  <!-- Generate the prereq element: -->
  <xsl:template name="prereq">
    <xsl:variable name="matched" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Prerequisites']]" />
    <xsl:if test="$matched != ''">
      <xsl:element name="prereq">
        <xsl:apply-templates select="$matched" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Generate the context element: -->
  <xsl:template name="context">
    <xsl:variable name="matched" select="p[@outputclass='title'][1]/preceding-sibling::*" />
    <xsl:if test="$matched != ''">
      <xsl:element name="context">
        <xsl:apply-templates select="$matched" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Generate the steps element: -->
  <xsl:template name="steps">
    <xsl:variable name="matched" select="*[(self::ol or self::ul) and preceding-sibling::p[@outputclass='title'][1][b='Procedure']][1]" />
    <xsl:if test="$matched != ''">
      <xsl:element name="steps">
        <xsl:for-each select="$matched/li">
          <xsl:call-template name="step" />
        </xsl:for-each>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Generate the result element: -->
  <xsl:template name="result">
    <xsl:variable name="matched" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Verification']]" />
    <xsl:if test="$matched != ''">
      <xsl:element name="result">
        <xsl:apply-templates select="$matched" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Generate the tasktroubleshooting element: -->
  <xsl:template name="tasktroubleshooting">
    <xsl:variable name="matched" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Troubleshooting' or b='Troubleshooting steps']]" />
    <xsl:if test="$matched != ''">
      <xsl:element name="tasktroubleshooting">
        <xsl:apply-templates select="$matched" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Generate the postreq element: -->
  <xsl:template name="postreq">
    <xsl:variable name="matched" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Next steps' or b='Next step']]" />
    <xsl:if test="$matched != ''">
      <xsl:element name="postreq">
        <xsl:apply-templates select="$matched" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Generate step elements: -->
  <xsl:template name="step">
    <xsl:element name="step">
      <!-- Wrap the first paragraph in the cmd element: -->
      <xsl:call-template name="cmd" />

      <!-- Wrap the rest of the content in the info and substeps
           elements: -->
      <xsl:call-template name="info" />
    </xsl:element>
  </xsl:template>

  <!-- Generate the cmd elements: -->
  <xsl:template name="cmd">
    <xsl:element name="cmd">
      <xsl:choose>
        <xsl:when test="text() != ''">
          <xsl:apply-templates select="./text()|./*" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="*[1]/text()|*[1]/*" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <!-- Generate the info and substeps elements: -->
  <xsl:template name="info">
    <xsl:if test="not(text())">
      <xsl:variable name="substeps" select="count(ol)" />
      <xsl:variable name="headinfo" select="*[position() > 1 and following-sibling::ol[$substeps]]" />

      <!-- Wrap the remaining elements into the info element if substeps
           are not present: -->
      <xsl:if test="count(*) > 1 and $substeps = 0">
        <xsl:element name="info">
          <xsl:apply-templates select="*[1]/following-sibling::*" />
        </xsl:element>
      </xsl:if>

      <!-- Wrap the remaining elements up to the first substeps in the
           info element: -->
      <xsl:if test="$headinfo != ''">
        <xsl:element name="info">
          <xsl:copy-of select="*[position() > 1 and following-sibling::ol[$substeps]]" />
        </xsl:element>
      </xsl:if>

      <!-- Process the substeps: -->
      <xsl:for-each select="ol">
        <xsl:variable name="position" select="position()" />

        <!-- Generate the substeps element: -->
        <xsl:element name="substeps">
          <xsl:for-each select="li">
            <xsl:call-template name="substep" />
          </xsl:for-each>
        </xsl:element>

        <xsl:choose>
          <!-- Wrap elements between substeps elements in the info
               element: -->
          <xsl:when test="following-sibling::ol">
            <xsl:element name="info">
              <xsl:apply-templates select="following-sibling::*[following-sibling::ol[$substeps - $position]]"/>
            </xsl:element>
          </xsl:when>
          <!-- Wrap elements after the last substeps element in the info
               element: -->
          <xsl:otherwise>
            <xsl:variable name="tailinfo" select="following-sibling::*" />
            <xsl:if test="$tailinfo != ''">
              <xsl:element name="info">
                <xsl:apply-templates select="$tailinfo" />
              </xsl:element>
            </xsl:if>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>

  <!-- Generate the substep elements: -->
  <xsl:template name="substep">
    <xsl:element name="substep">
      <!-- Wrap the first paragraph in the cmd element: -->
      <xsl:call-template name="cmd" />

      <!-- Wrap the remaining elements into the info element: -->
      <xsl:if test="not(text()) and count(*) > 1">
        <xsl:element name="info">
          <xsl:apply-templates select="*[1]/following-sibling::*" />
        </xsl:element>
      </xsl:if>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>

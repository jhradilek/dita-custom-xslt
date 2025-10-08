<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2024, 2025 Jaromir Hradilek

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
  <xsl:preserve-space elements="codeblock pre screen" />

  <!-- Report an error if the converted file is not a DITA topic: -->
  <xsl:template match="/*[not(self::topic)]">
    <xsl:message terminate="yes">ERROR: Not a DITA topic</xsl:message>
  </xsl:template>

  <!-- Report an error if the converted file contains a section: -->
  <xsl:template match="//section">
    <xsl:message terminate="yes">ERROR: Section not allowed in a DITA task</xsl:message>
  </xsl:template>

  <!-- Remove the outputclass attribute from the root element: -->
  <xsl:template match="/topic/@outputclass" />

  <!-- Prevent duplication of the abstract paragraph (used for shortdesc): -->
  <xsl:template match="//body/p[1][@outputclass='abstract']" />

  <!-- Prevent duplication of the example section: -->
  <xsl:template match="//body/example" />

  <!-- Issue a warning if the converted file contains multiple examples: -->
  <xsl:template match="//body/example[2]">
    <xsl:message terminate="no">WARNING: Extra example elements found, skipping...</xsl:message>
  </xsl:template>

  <!-- Perform identity transformation: -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <!-- Transform the root element: -->
  <xsl:template match="/topic">
    <xsl:element name="task">
      <xsl:apply-templates select="@*|node()" />
    </xsl:element>
  </xsl:template>

  <!-- Transform the body element: -->
  <xsl:template match="body">
    <!-- Compose the shortdesc element: -->
    <xsl:call-template name="shortdesc">
      <xsl:with-param name="contents" select="p[1][@outputclass='abstract']" />
    </xsl:call-template>
    <xsl:element name="taskbody">
      <!-- Compose the prereq element: -->
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'prereq'" />
        <xsl:with-param name="contents" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Prerequisite' or b='Prerequisites']]" />
      </xsl:call-template>
      <!-- Compose the context element: -->
      <xsl:choose>
        <xsl:when test="p[@outputclass='title']">
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'context'" />
            <xsl:with-param name="contents" select="p[@outputclass='title'][1]/preceding-sibling::*" />
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'context'" />
            <xsl:with-param name="contents" select="*" />
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
      <!-- Compose the steps element: -->
      <xsl:call-template name="steps">
        <xsl:with-param name="contents" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Procedure']]" />
      </xsl:call-template>
      <!-- Compose the result element: -->
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'result'" />
        <xsl:with-param name="contents" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Verification' or b='Result' or b='Results']]" />
      </xsl:call-template>
      <!-- Compose the tasktroubleshooting element: -->
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'tasktroubleshooting'" />
        <xsl:with-param name="contents" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Troubleshooting' or b='Troubleshooting step' or b='Troubleshooting steps']]" />
      </xsl:call-template>
      <!-- Compose the example element: -->
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'example'" />
        <xsl:with-param name="contents" select="//body/example[1]/*|//body/example[1]/@*" />
      </xsl:call-template>
      <!-- Compose the postreq element: -->
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'postreq'" />
        <xsl:with-param name="contents" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Next step' or b='Next steps']]" />
      </xsl:call-template>
    </xsl:element>
    <!-- Compose the related-links element: -->
    <xsl:call-template name="related-links">
        <xsl:with-param name="contents" select="*[not(@outputclass='title') and preceding-sibling::p[@outputclass='title'][1][b='Additional resources']]" />
    </xsl:call-template>

    <!-- Issue a warning if the converted file contains an unsupported title: -->
    <xsl:for-each select="p[@outputclass='title']/b/text()">
      <xsl:variable name="titles" select="'|Prerequisite|Prerequisites|Procedure|Verification|Result|Results|Troubleshooting|Troubleshooting step|Troubleshooting steps|Next step|Next steps|Additional resources|'" />
      <xsl:if test="not(contains($titles, concat('|', ., '|')))">
        <xsl:message terminate="no">WARNING: Unsupported title '<xsl:copy-of select="." />' found, skipping...</xsl:message>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- Compose the steps element: -->
  <xsl:template name="steps">
    <xsl:param name="contents" />
    <xsl:variable name="list" select="$contents[self::ol or self::ul][1]" />
    <xsl:if test="$contents">
      <xsl:if test="$contents[self::section]">
        <xsl:message terminate="yes">ERROR: Section not allowed in a DITA task</xsl:message>
      </xsl:if>
      <xsl:if test="$contents[not(self::ol or self::ul or self::example)]">
        <xsl:message terminate="no">WARNING: Non-list elements found in steps, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="$contents[self::ol or self::ul][2]">
        <xsl:message terminate="no">WARNING: Extra list elements found in steps, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="not($list)">
        <xsl:message terminate="no">WARNING: No list elements found in steps</xsl:message>
      </xsl:if>
      <xsl:if test="$contents//example/title">
        <xsl:message terminate="no">WARNING: Title found in stepxmp, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="$list">
        <xsl:variable name="name">
          <xsl:choose>
            <xsl:when test="$list[self::ul]">
              <xsl:text>steps-unordered</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>steps</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:element name="{$name}">
          <xsl:call-template name="universal-attributes">
            <xsl:with-param name="attributes" select="$list/@*" />
          </xsl:call-template>
          <xsl:for-each select="$list/li">
            <xsl:call-template name="step-substep">
              <xsl:with-param name="type" select="'step'" />
            </xsl:call-template>
          </xsl:for-each>
        </xsl:element>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <!-- Include the common templates: -->
  <xsl:include href="common-templates.xsl" />

</xsl:stylesheet>

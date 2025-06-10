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

  <!-- Define a list of valid cmd element children: -->
  <xsl:variable name="cmd-children" select="' abbreviated-form apiname b boolean cite cmdname codeph data data-about draft-comment equation-inline filepath fn foreign i image indexterm indextermref keyword line-through markupname mathml menucascade msgnum msgph numcharref option overline parameterentity parmname ph q required-cleanup sort-as state sub sup svg-container synph systemoutput term text textentity tm tt u uicontrol unknown userinput varname wintitle xmlatt xmlelement xmlnsname xmlpi xref '" />

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

  <!-- Compose the shortdesc element: -->
  <xsl:template name="shortdesc">
    <xsl:param name="contents" />
    <xsl:if test="$contents">
      <xsl:element name="shortdesc">
        <xsl:apply-templates select="$contents/text()|$contents/*" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Compose the steps element: -->
  <xsl:template name="steps">
    <xsl:param name="contents" />
    <xsl:variable name="list" select="$contents[self::ol or self::ul][1]" />
    <xsl:if test="$contents">
      <xsl:if test="$contents[self::section]">
        <xsl:message terminate="yes">ERROR: Section not allowed in a DITA task</xsl:message>
      </xsl:if>
      <xsl:if test="$contents[not(self::ol or self::ul)]">
        <xsl:message terminate="no">WARNING: Non-list elements found in steps, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="$contents[self::ol or self::ul][2]">
        <xsl:message terminate="no">WARNING: Extra list elements found in steps, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="not($list)">
        <xsl:message terminate="no">WARNING: No list elements found in steps</xsl:message>
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
          <xsl:for-each select="$list/li">
            <xsl:call-template name="step-substep">
              <xsl:with-param name="type" select="'step'" />
            </xsl:call-template>
          </xsl:for-each>
        </xsl:element>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <!-- Compose the step/substep element: -->
  <xsl:template name="step-substep">
    <xsl:param name="type" />
    <xsl:element name="{$type}">
      <xsl:choose>
        <xsl:when test="text()">
          <xsl:variable name="info-element" select="*[not(contains($cmd-children, concat(' ', name(), ' ')))][1]" />
          <xsl:choose>
            <xsl:when test="$info-element">
              <xsl:call-template name="compose-element">
                <xsl:with-param name="name" select="'cmd'" />
                <xsl:with-param name="contents" select="$info-element/preceding-sibling::*|$info-element/preceding-sibling::text()" />
              </xsl:call-template>
              <xsl:call-template name="info">
                <xsl:with-param name="parent" select="$type" />
                <xsl:with-param name="contents" select="$info-element|$info-element/following-sibling::*|$info-element/following-sibling::text()" />
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="compose-element">
                <xsl:with-param name="name" select="'cmd'" />
                <xsl:with-param name="contents" select="text()|*" />
              </xsl:call-template>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'cmd'" />
            <xsl:with-param name="contents" select="*[1]/text()|*[1]/*" />
          </xsl:call-template>
          <xsl:if test="*[2]">
            <xsl:call-template name="info">
              <xsl:with-param name="parent" select="$type" />
              <xsl:with-param name="contents" select="*[position() > 1]" />
            </xsl:call-template>
          </xsl:if>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <!-- Compose the info element: -->
  <xsl:template name="info">
    <xsl:param name="parent" />
    <xsl:param name="contents" />
    <xsl:choose>
      <xsl:when test="$parent = 'step'">
        <xsl:call-template name="info-substeps">
          <xsl:with-param name="contents" select="$contents" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="compose-element">
          <xsl:with-param name="name" select="'info'" />
          <xsl:with-param name="contents" select="$contents" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Compose alternating info/substeps elements: -->
  <xsl:template name="info-substeps">
    <xsl:param name="contents" />
    <xsl:variable name="substeps-count" select="count($contents[self::ol])" />
    <xsl:variable name="first-info" select="$contents[following-sibling::ol[$substeps-count]]" />
    <xsl:if test="$substeps-count = 0">
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'info'" />
        <xsl:with-param name="contents" select="$contents" />
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="$first-info">
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'info'" />
        <xsl:with-param name="contents" select="$first-info" />
      </xsl:call-template>
    </xsl:if>
    <xsl:for-each select="$contents[self::ol]">
      <xsl:variable name="current-position" select="position()" />
      <xsl:element name="substeps">
        <xsl:for-each select="li">
          <xsl:call-template name="step-substep">
            <xsl:with-param name="type" select="'substep'" />
          </xsl:call-template>
        </xsl:for-each>
      </xsl:element>
      <xsl:choose>
        <xsl:when test="following-sibling::ol">
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'info'" />
            <xsl:with-param name="contents" select="following-sibling::*[following-sibling::ol[$substeps-count - $current-position]]" />
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="last-info" select="following-sibling::*|following-sibling::text()" />
          <xsl:if test="$last-info">
            <xsl:call-template name="compose-element">
              <xsl:with-param name="name" select="'info'" />
              <xsl:with-param name="contents" select="$last-info" />
            </xsl:call-template>
          </xsl:if>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <!-- Compose the related-links element: -->
  <xsl:template name="related-links">
    <xsl:param name="contents" />
    <xsl:variable name="list" select="$contents[self::ul][1]" />
    <xsl:if test="$contents">
      <xsl:if test="$contents[not(self::ul)]">
        <xsl:message terminate="no">WARNING: Non-list elements found in related links, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="$contents[self::ul][2]">
        <xsl:message terminate="no">WARNING: Extra list elements found in related-links, skipping...</xsl:message>
      </xsl:if>
      <xsl:if test="not($list)">
        <xsl:message terminate="no">WARNING: No list elements found in related links</xsl:message>
      </xsl:if>
      <xsl:element name="related-links">
        <xsl:for-each select="$list/li">
          <xsl:choose>
            <xsl:when test="not(xref)">
              <xsl:message terminate="no">WARNING: Unexpected content found in related-links, skipping...</xsl:message>
            </xsl:when>
            <xsl:otherwise>
              <xsl:if test="count(*) &gt; 1 or text()">
              <xsl:message terminate="no">WARNING: Unexpected content found in related-links, skipping...</xsl:message>
              </xsl:if>
              <xsl:element name="link">
                <xsl:copy-of select="xref/@*" />
                <xsl:if test="xref/text()">
                  <xsl:element name="linktext">
                    <xsl:apply-templates select="xref/text()" />
                  </xsl:element>
                </xsl:if>
              </xsl:element>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Helper: Compose an element with the given name and contents: -->
  <xsl:template name="compose-element">
    <xsl:param name="name" />
    <xsl:param name="contents" />
    <xsl:if test="$contents">
      <xsl:element name="{$name}">
        <xsl:apply-templates select="$contents" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>

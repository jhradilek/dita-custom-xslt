<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2024, 2025 Jaromir Hradilek

  A custom XSLT stylesheet to convert a generic DITA topic to a specialized
  DITA task topic:

    1. Any contents preceding the first ordered list is  considered part of
       the <context> element.
    2. The first ordered list is transformed into <steps>.
    3. Any contents between the first ordered list and the first example is
       considered part of the <result> element.
    4. The first <example> is used as is.
    5. Any contents following the first example is  considered  part of the
       <postreq> element.

  Sections are not permitted and will result in an error. Multiple examples
  are not permitted and will result in an error.

  Usage: xsltproc ––novalid task.xsl YOUR_TOPIC.dita

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

  <!-- Report an error if the converted file contains multiple examples: -->
  <xsl:template match="//body/example[2]">
    <xsl:message terminate="yes">ERROR: Multiple examples not allowed in a DITA task</xsl:message>
  </xsl:template>

  <!-- Define a list of valid cmd element children: -->
  <xsl:variable name="cmd-children" select="' abbreviated-form apiname b boolean cite cmdname codeph data data-about draft-comment equation-inline filepath fn foreign i image indexterm indextermref keyword line-through markupname mathml menucascade msgnum msgph numcharref option overline parameterentity parmname ph q required-cleanup sort-as state sub sup svg-container synph systemoutput term text textentity tm tt u uicontrol unknown userinput varname wintitle xmlatt xmlelement xmlnsname xmlpi xref '" />

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
    <xsl:element name="taskbody">
      <xsl:variable name="steps" select="ol[1]" />
      <xsl:variable name="example" select="example[1]" />
      <xsl:call-template name="context">
        <xsl:with-param name="steps" select="$steps" />
        <xsl:with-param name="example" select="$example" />
      </xsl:call-template>
      <xsl:call-template name="steps">
        <xsl:with-param name="steps" select="$steps" />
      </xsl:call-template>
      <xsl:call-template name="result">
        <xsl:with-param name="steps" select="$steps" />
        <xsl:with-param name="example" select="$example" />
      </xsl:call-template>
      <xsl:call-template name="example">
        <xsl:with-param name="example" select="$example" />
      </xsl:call-template>
      <xsl:call-template name="postreq">
        <xsl:with-param name="example" select="$example" />
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <!-- Compose the context element: -->
  <xsl:template name="context">
    <xsl:param name="steps" />
    <xsl:param name="example" />
    <xsl:choose>
      <xsl:when test="$steps">
        <xsl:call-template name="compose-element">
          <xsl:with-param name="name" select="'context'" />
          <xsl:with-param name="contents" select="ol[1]/preceding-sibling::*" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$example">
        <xsl:call-template name="compose-element">
          <xsl:with-param name="name" select="'context'" />
          <xsl:with-param name="contents" select="example[1]/preceding-sibling::*" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="compose-element">
          <xsl:with-param name="name" select="'context'" />
          <xsl:with-param name="contents" select="*" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- Compose the steps element: -->
  <xsl:template name="steps">
    <xsl:param name="steps" />
    <xsl:if test="$steps">
      <xsl:element name="steps">
        <xsl:for-each select="$steps/li">
          <xsl:call-template name="step-substep">
            <xsl:with-param name="type" select="'step'" />
          </xsl:call-template>
        </xsl:for-each>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <!-- Compose the result element: -->
  <xsl:template name="result">
    <xsl:param name="steps" />
    <xsl:param name="example" />
    <xsl:if test="$steps">
      <xsl:choose>
        <xsl:when test="$example">
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'result'" />
            <xsl:with-param name="contents" select="*[not(self::example) and preceding-sibling::ol[1] and following-sibling::example[1]]" />
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'result'" />
            <xsl:with-param name="contents" select="ol[1]/following-sibling::*" />
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- Compose the example element: -->
  <xsl:template name="example">
    <xsl:param name="example" />
    <xsl:if test="$example">
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'example'" />
        <xsl:with-param name="contents" select="example[1]/*|example[1]/@*" />
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- Compose the postreq element: -->
  <xsl:template name="postreq">
    <xsl:variable name="postreq" select="example[1]/following-sibling::*" />
    <xsl:if test="$postreq">
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'postreq'" />
        <xsl:with-param name="contents" select="$postreq" />
      </xsl:call-template>
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

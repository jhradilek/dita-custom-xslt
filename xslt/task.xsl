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
      <xsl:if test="$steps//example/title">
        <xsl:message terminate="no">WARNING: Title found in stepxmp, skipping...</xsl:message>
      </xsl:if>
      <xsl:element name="steps">
        <xsl:call-template name="universal-attributes">
          <xsl:with-param name="attributes" select="$steps/@*" />
        </xsl:call-template>
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

  <!-- Include the common templates: -->
  <xsl:include href="common-templates.xsl" />

</xsl:stylesheet>

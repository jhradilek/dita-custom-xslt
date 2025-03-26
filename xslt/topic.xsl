<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2025 Jaromir Hradilek

  A custom XSLT stylesheet to convert nested sections to nested topics in a
  monolithic  DITA  topic  generated  with   the  asciidoctor-dita-topic[1]
  plug-in.

  Usage: xsltproc ––novalid topic.xsl YOUR_TOPIC.dita

  [1] https://github.com/jhradilek/asciidoctor-dita-topic

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
  <xsl:output encoding="utf-8" method="xml" doctype-system="reference.dtd" doctype-public="-//OASIS//DTD DITA Reference//EN" />

  <!-- Format the XML output: -->
  <xsl:output indent="yes" />
  <xsl:strip-space elements="*" />
  <xsl:preserve-space elements="codeblock pre screen" />

  <!-- Report an error if the converted file is not a DITA topic: -->
  <xsl:template match="/*[not(self::topic)]">
    <xsl:message terminate="yes">ERROR: Not a DITA topic</xsl:message>
  </xsl:template>

  <!-- Perform identity transformation: -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <!-- Transform the root element: -->
  <xsl:template match="/topic">
    <xsl:element name="topic">
      <xsl:apply-templates select="@*" />
      <xsl:apply-templates select="body/preceding-sibling::*" />
      <xsl:if test="body/section[1]/preceding-sibling::*">
        <xsl:element name="body">
          <xsl:apply-templates select="body/@*" />
          <xsl:choose>
            <xsl:when test="body/section">
              <xsl:apply-templates select="body/section[1]/preceding-sibling::*" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="*" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:element>
      </xsl:if>
      <xsl:for-each select="body/section">
        <xsl:call-template name="compose-topic">
          <xsl:with-param name="attributes" select="@*" />
          <xsl:with-param name="contents" select="." />
        </xsl:call-template>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <!-- Compose the topic element: -->
  <xsl:template name="compose-topic">
    <xsl:param name="attributes" />
    <xsl:param name="contents" />
    <xsl:if test="$contents">
      <xsl:element name="topic">
        <xsl:apply-templates select="$attributes" />
        <xsl:element name="title">
          <xsl:apply-templates select="$contents/title/@*" />
          <xsl:apply-templates select="$contents/title/text()|$contents/title/*" />
        </xsl:element>
        <xsl:element name="body">
          <xsl:choose>
            <xsl:when test="$contents/section">
              <xsl:apply-templates select="$contents/section[1]/preceding-sibling::*[not(self::title)]" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="$contents/*[not(self::title)]" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:element>
        <xsl:for-each select="$contents/section">
          <xsl:call-template name="compose-topic">
            <xsl:with-param name="attributes" select="@*" />
            <xsl:with-param name="contents" select="." />
          </xsl:call-template>
        </xsl:for-each>
      </xsl:element>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>

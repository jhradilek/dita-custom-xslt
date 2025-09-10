<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2025 Jaromir Hradilek

  A custom XSLT stylesheet  to convert  a  monolithic DITA topic  generated
  with  the  asciidoctor-dita-topic[1] plug-in  and pre-processed with  the
  single-topic.xsl stylesheet to a DITA map.

  IMPORTANT: The stylesheet assumes that all topic elements have a valid,
             unique ID attribute defined.

  Usage: xsltproc ––novalid single-map.xsl YOUR_TOPIC.dita

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
  <xsl:output encoding="utf-8" method="xml" doctype-system="map.dtd" doctype-public="-//OASIS//DTD DITA Map//EN" />

  <!-- Format the XML output: -->
  <xsl:output indent="yes" />
  <xsl:strip-space elements="*" />

  <!-- Report an error if the converted file is not a DITA topic: -->
  <xsl:template match="/*[not(self::topic)]">
    <xsl:message terminate="yes">ERROR: Not a DITA topic</xsl:message>
  </xsl:template>

  <!-- Transform the root element: -->
  <xsl:template match="/topic">
    <xsl:element name="map">
      <xsl:call-template name="compose-topicref">
          <xsl:with-param name="id" select="@id" />
          <xsl:with-param name="contents" select="." />
          <xsl:with-param name="type" select="@outputclass" />
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <!-- Compose the topicref element: -->
  <xsl:template name="compose-topicref">
    <xsl:param name="id" />
    <xsl:param name="type" />
    <xsl:param name="contents" />
    <xsl:element name="topicref">
      <xsl:attribute name="href"><xsl:value-of select="concat($id, '.dita')" /></xsl:attribute>
      <xsl:choose>
        <xsl:when test="contains('|concept|reference|task|', concat('|', $type, '|'))">
          <xsl:attribute name="type"><xsl:value-of select="$type" /></xsl:attribute>
        </xsl:when>
        <xsl:when test="$type = 'procedure'">
          <xsl:attribute name="type">task</xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="type">concept</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:for-each select="./topic">
        <xsl:call-template name="compose-topicref">
          <xsl:with-param name="id" select="@id" />
          <xsl:with-param name="type" select="@outputclass" />
          <xsl:with-param name="contents" select="." />
        </xsl:call-template>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>

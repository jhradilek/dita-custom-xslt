<?xml version='1.0' encoding='utf-8' ?>

<!--
  Copyright (C) 2024, 2025 Jaromir Hradilek

  A collection of XSLT templates used by the remaining XSLT stylesheets.

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
  <!-- Define the list of valid cmd element children: -->
  <xsl:variable name="cmd-children" select="' abbreviated-form apiname b boolean cite cmdname codeph data data-about draft-comment equation-inline filepath fn foreign i image indexterm indextermref keyword line-through markupname mathml menucascade msgnum msgph numcharref option overline parameterentity parmname ph q required-cleanup sort-as state sub sup svg-container synph systemoutput term text textentity tm tt u uicontrol unknown userinput varname wintitle xmlatt xmlelement xmlnsname xmlpi xref '" />

  <!-- Define the list of supported attributes from the universal attribute group: -->
  <xsl:variable name="universal-attribute-group" select="' id props base platform product audience otherprops deliveryTarget importance rev status translate xml:lang dir '" />

  <!-- Compose the step/substep element: -->
  <xsl:template name="step-substep">
    <xsl:param name="type" />
    <xsl:element name="{$type}">
      <xsl:call-template name="universal-attributes">
        <xsl:with-param name="attributes" select="@*" />
      </xsl:call-template>
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
            <xsl:with-param name="attributes" select="*[1]/@*" />
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
        <xsl:call-template name="info-stepxmp">
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
      <xsl:call-template name="info-stepxmp">
        <xsl:with-param name="contents" select="$contents" />
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="$first-info">
      <xsl:call-template name="info-stepxmp">
        <xsl:with-param name="contents" select="$first-info" />
      </xsl:call-template>
    </xsl:if>
    <xsl:for-each select="$contents[self::ol]">
      <xsl:variable name="current-position" select="position()" />
      <xsl:element name="substeps">
        <xsl:call-template name="universal-attributes">
          <xsl:with-param name="attributes" select="@*" />
        </xsl:call-template>
        <xsl:for-each select="li">
          <xsl:call-template name="step-substep">
            <xsl:with-param name="type" select="'substep'" />
          </xsl:call-template>
        </xsl:for-each>
      </xsl:element>
      <xsl:choose>
        <xsl:when test="following-sibling::ol">
          <xsl:call-template name="info-stepxmp">
            <xsl:with-param name="contents" select="following-sibling::*[following-sibling::ol[$substeps-count - $current-position]]" />
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="last-info" select="following-sibling::*|following-sibling::text()" />
          <xsl:if test="$last-info">
            <xsl:call-template name="info-stepxmp">
              <xsl:with-param name="contents" select="$last-info" />
            </xsl:call-template>
          </xsl:if>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <!-- Compose alternating info/stepxmp elements: -->
  <xsl:template name="info-stepxmp">
    <xsl:param name="contents" />
    <xsl:variable name="xmp-count" select="count($contents[self::example])" />
    <xsl:variable name="first-info" select="$contents[following-sibling::example[$xmp-count]]" />
    <xsl:if test="$xmp-count = 0">
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
    <xsl:for-each select="$contents[self::example]">
      <xsl:variable name="current-position" select="position()" />
      <xsl:call-template name="compose-element">
        <xsl:with-param name="name" select="'stepxmp'" />
        <xsl:with-param name="contents" select="text()|*[not(self::title)]" />
        <xsl:with-param name="attributes" select="@*" />
      </xsl:call-template>
      <xsl:choose>
        <xsl:when test="following-sibling::example">
          <xsl:call-template name="compose-element">
            <xsl:with-param name="name" select="'info'" />
            <xsl:with-param name="contents" select="following-sibling::*[following-sibling::example[$xmp-count - $current-position]]" />
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="last-info" select="following-sibling::*[not(self::ol)]|following-sibling::text()" />
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

  <!-- Compose the shortdesc element: -->
  <xsl:template name="shortdesc">
    <xsl:param name="contents" />
    <xsl:call-template name="compose-element">
      <xsl:with-param name="name" select="'shortdesc'" />
      <xsl:with-param name="contents" select="$contents/text()|$contents/*" />
      <xsl:with-param name="attributes" select="$contents/@*" />
    </xsl:call-template>
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
        <xsl:call-template name="universal-attributes">
          <xsl:with-param name="attributes" select="$list/@*" />
        </xsl:call-template>
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

  <!-- Helper: Copy the universal attribute group: -->
  <xsl:template name="universal-attributes">
    <xsl:param name="attributes" />
    <xsl:for-each select="$attributes">
      <xsl:if test="contains($universal-attribute-group, concat(' ', name(), ' '))">
        <xsl:copy-of select="." />
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <!-- Helper: Compose an element with the given name and contents: -->
  <xsl:template name="compose-element">
    <xsl:param name="name" />
    <xsl:param name="contents" />
    <xsl:param name="attributes" />
    <xsl:if test="$contents">
      <xsl:element name="{$name}">
        <xsl:if test="$attributes">
          <xsl:call-template name="universal-attributes">
            <xsl:with-param name="attributes" select="$attributes" />
          </xsl:call-template>
        </xsl:if>
        <xsl:apply-templates select="$contents" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>

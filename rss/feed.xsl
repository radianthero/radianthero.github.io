<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  exclude-result-prefixes="xsl">

  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  
  <!-- Match the root element of the RSS feed -->
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
        <title>Web Feed <xsl:value-of select="rss/channel/title"/></title>
        <style type="text/css">
          body{max-width:768px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5em}section{margin:30px 15px}h1{font-size:2em;margin:.67em 0;line-height:1.125em}h2{border-bottom:1px solid #eaecef;padding-bottom:.3em}.alert{background:#fff5b1;padding:4px 12px;margin:0 -12px}a{text-decoration:none}.entry h3{margin-bottom:0}.entry p{margin:4px 0}
        </style>
      </head>
      <body>
        <section>
          <div class="alert">
            <p><strong>This is a web feed</strong>, also known as an RSS feed. <strong>Subscribe</strong> by copying the URL from the address bar into an RSS reader, I recommend Feeder, Raven Reader, or NetNewsWire.</p>
          </div>
        </section>
        <section>
          <xsl:apply-templates select="rss/channel" />
        </section>
        <section>
          <h2>Recent Items</h2>
          <xsl:apply-templates select="rss/channel/item" />
        </section>
      </body>
    </html>
  </xsl:template>

  <!-- Match the RSS channel element -->
  <xsl:template match="rss/channel">
    <h1>Radiant Ink's Web Feed Preview</h1>
    <p>This RSS feed provides the latest posts from Radiant Ink.</p>
  </xsl:template>

  <!-- Match the RSS item element -->
  <xsl:template match="rss/channel/item">
    <div class="entry">
      <h3>
        <a href="{link}" target="_blank">
          <xsl:value-of select="title"/>
        </a>
      </h3>
      <p>
        <xsl:value-of select="description" />
      </p>
      <small>
        Published: <xsl:value-of select="pubDate" />
      </small>
    </div>
  </xsl:template>

</xsl:stylesheet>

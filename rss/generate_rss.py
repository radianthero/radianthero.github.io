import os
import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import quote

# Configuration
SITE_URL = "https://example.com"  # Update with your site URL
OUTPUT_FILE = "feed.xml"
XSLT_FILE = "feed.xsl"  # Path to the XSLT file
SEARCH_DIRECTORIES = [
    "../blog",
    "../port/",
    "../tut/"
]

def encode_url(url):
    """Encodes spaces and special characters in a URL."""
    return quote(url, safe="/:")

def escape_text(text):
    """Escapes reserved XML characters in a text."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )

def extract_metadata(file_path):
    """Extracts metadata like title and description from an HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        title = soup.title.string if soup.title else "Untitled"
        description_meta = soup.find("meta", attrs={"name": "description"})
        description = description_meta["content"] if description_meta else "Description not provided."
        return escape_text(title), escape_text(description)

def generate_rss():
    """Generates an RSS feed based on HTML files from multiple directories."""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # Add basic channel info
    ET.SubElement(channel, "title").text = "Your Website Title"  # Update as needed
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "Your website description"  # Update as needed
    ET.SubElement(channel, "language").text = "en-US"  # Update language as needed

    # Use timezone-aware datetime
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Scan directories for HTML files
    for directory in SEARCH_DIRECTORIES:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue
        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".html"):
                    file_path = os.path.join(root, file_name)
                    title, description = extract_metadata(file_path)
                    relative_path = os.path.relpath(file_path, start=directory)
                    link = f"{SITE_URL}/{relative_path.replace(os.sep, '/')}"
                    link = encode_url(link)  # Encode URL

                    # Use timezone-aware datetime for pubDate
                    pub_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

                    # Create RSS item
                    item = ET.SubElement(channel, "item")
                    ET.SubElement(item, "title").text = title
                    ET.SubElement(item, "link").text = link
                    ET.SubElement(item, "description").text = description
                    ET.SubElement(item, "pubDate").text = pub_date

                    # Add guid with isPermaLink="true"
                    guid = ET.SubElement(item, "guid")
                    guid.text = link
                    guid.set("isPermaLink", "true")

    # Convert to string and add the XSLT directive
    rss_tree = ET.ElementTree(rss)
    rss_string = ET.tostring(rss, encoding="unicode")
    xslt_directive = f'<?xml-stylesheet type="text/xsl" href="{XSLT_FILE}"?>\n'

    # Write the feed with the XSLT directive
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(xslt_directive)
            file.write(rss_string)
        print(f"RSS feed generated: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing feed.xml: {e}")

# Run the script
if __name__ == "__main__":
    generate_rss()

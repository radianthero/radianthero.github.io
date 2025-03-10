import os
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import html

# Configuration
SITE_URL = "https://www.radiant-ink.com"  # Correct domain for your website
OUTPUT_FILE = "feed.xml"
XSLT_FILE = "feed.xsl"  # Path to the XSLT file
SEARCH_DIRECTORIES = [
    "../blog",
    "../port/",
    "../tut/"
]
TRACKER_FILE = "processed_files.txt"  # File to track processed items

def encode_url(url):
    """Encodes spaces and special characters in a URL."""
    return quote(url, safe="/:")

def load_processed_items():
    """Loads the list of already processed items from the tracker file."""
    if not os.path.exists(TRACKER_FILE):
        return set()
    with open(TRACKER_FILE, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)

def save_processed_items(processed_items):
    """Saves the list of processed items to the tracker file."""
    with open(TRACKER_FILE, "w", encoding="utf-8") as file:
        for item in processed_items:
            file.write(item + "\n")

def extract_metadata(file_path):
    """Extracts metadata like title, description, and full content from an HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        
        # Extract the title
        title = soup.title.string if soup.title else "Untitled"
        
        # Extract description from meta tag
        description_meta = soup.find("meta", attrs={"name": "description"})
        description = description_meta["content"] if description_meta else "Description not provided."
        
        # Extract the thumbnail URL (using Open Graph or first image in the post)
        thumbnail_url = None
        thumbnail_meta = soup.find("meta", property="og:image")
        if thumbnail_meta:
            thumbnail_url = thumbnail_meta["content"]
        else:
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                img_src = img_tag["src"]
                if img_src.startswith("/"):
                    thumbnail_url = urljoin(SITE_URL, img_src)
                elif img_src.startswith("../"):
                    thumbnail_url = urljoin(SITE_URL, img_src.replace("../", ""))
                else:
                    thumbnail_url = img_src

        print(f"Extracted title: {title}")
        print(f"Extracted description: {description}")
        print(f"Extracted thumbnail URL: {thumbnail_url}")

        return title, description, thumbnail_url

def generate_rss():
    """Generates an RSS feed with basic metadata for new items only."""
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:media": "http://search.yahoo.com/mrss/"})
    channel = ET.SubElement(rss, "channel")

    # Add basic channel info
    ET.SubElement(channel, "title").text = "Radiant Ink"
    ET.SubElement(channel, "link").text = f"{SITE_URL}/feed.xml"
    ET.SubElement(channel, "description").text = "An art blog"
    ET.SubElement(channel, "language").text = "en-US"
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = f"{SITE_URL}/favicons/favicon-32x32.png"
    ET.SubElement(image, "title").text = "Radiant Ink"
    ET.SubElement(image, "link").text = SITE_URL

    processed_items = load_processed_items()
    new_items = set()

    for directory in SEARCH_DIRECTORIES:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue
        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".html"):
                    file_path = os.path.join(root, file_name)
                    file_path = file_path.replace("\\", "/")
                    relative_path = os.path.relpath(file_path, start=directory).replace("\\", "/")

                    if relative_path in processed_items:
                        continue

                    title, description, thumbnail_url = extract_metadata(file_path)

                    subdirectory = None
                    if "../port/" in file_path:
                        subdirectory = "port"
                    elif "../tut/" in file_path:
                        subdirectory = "tut"
                    elif "../blog/" in file_path:
                        subdirectory = "blog"

                    # Correctly construct the link
                    if subdirectory:
                        link = f"{SITE_URL}/{subdirectory}/{relative_path}"
                    else:
                        link = f"{SITE_URL}/{relative_path}"

                    link = encode_url(link)

                    # Ensure thumbnail URL is absolute
                    if thumbnail_url and not thumbnail_url.startswith("http"):
                        thumbnail_url = urljoin(SITE_URL, thumbnail_url)

                    pub_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

                    item = ET.SubElement(channel, "item")
                    ET.SubElement(item, "title").text = html.unescape(title) or "Untitled"
                    ET.SubElement(item, "link").text = link
                    ET.SubElement(item, "description").text = description or "No description available."
                    ET.SubElement(item, "pubDate").text = pub_date
                    guid = ET.SubElement(item, "guid")
                    guid.text = link
                    guid.set("isPermaLink", "true")

                    if thumbnail_url:
                        media_thumbnail = ET.SubElement(item, "{http://search.yahoo.com/mrss/}thumbnail")
                        media_thumbnail.set("url", encode_url(thumbnail_url))

                    new_items.add(relative_path)

    if not new_items:
        print("No new items to add to the RSS feed.")
        return

    rss_tree = ET.ElementTree(rss)
    rss_string = ET.tostring(rss, encoding="unicode")
    xslt_directive = f'<?xml-stylesheet type="text/xsl" href="{XSLT_FILE}"?>\n'

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(xslt_directive)
            file.write(rss_string)
        print(f"RSS feed generated: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing feed.xml: {e}")

    processed_items.update(new_items)
    save_processed_items(processed_items)

if __name__ == "__main__":
    generate_rss()

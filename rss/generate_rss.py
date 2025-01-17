import os
import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import quote

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

def escape_text(text):
    """Escapes reserved XML characters in a text."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )

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
    """Extracts metadata like title, description, and thumbnail from an HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        title = soup.title.string if soup.title else "Untitled"
        description_meta = soup.find("meta", attrs={"name": "description"})
        description = description_meta["content"] if description_meta else "Description not provided."
        
        # Extract thumbnail from <meta property="og:image">
        thumbnail_meta = soup.find("meta", property="og:image")
        thumbnail_url = thumbnail_meta["content"] if thumbnail_meta else None
        
        return escape_text(title), escape_text(description), thumbnail_url

def generate_rss():
    """Generates an RSS feed with thumbnails for new items only."""
    rss = ET.Element("rss", version="2.0", xmlns_media="http://search.yahoo.com/mrss/")
    channel = ET.SubElement(rss, "channel")

    # Add basic channel info
    ET.SubElement(channel, "title").text = "Radiant Ink"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "An art blog"
    ET.SubElement(channel, "language").text = "en-US"
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Load processed items
    processed_items = load_processed_items()
    new_items = set()

    # Scan directories for HTML files
    for directory in SEARCH_DIRECTORIES:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue
        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".html"):
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, start=directory)

                    # Use relative_path as a unique identifier
                    if relative_path in processed_items:
                        continue  # Skip already processed items

                    # Extract metadata and generate RSS item
                    title, description, thumbnail_url = extract_metadata(file_path)
                    
                    # Determine the subdirectory and prepend it to the link
                    subdirectory = None
                    for directory in SEARCH_DIRECTORIES:
                        if file_path.startswith(os.path.join(directory, "")):
                            subdirectory = os.path.relpath(file_path, start=directory).split(os.sep, 1)[0]
                            break

                    # Debug: Print the subdirectory found
                    print(f"Subdirectory: {subdirectory}")
                    
                    # Ensure the relative_path includes the subdirectory
                    relative_path = relative_path.replace(os.sep, '/')

                    # Debug: Print the relative path before finalizing the link
                    print(f"Relative path: {relative_path}")

                    if subdirectory:
                        link = f"{SITE_URL}/{subdirectory}/{relative_path}"
                    else:
                        link = f"{SITE_URL}/{relative_path}"

                    # Debug: Print the final constructed link
                    print(f"Final link: {link}")

                    link = f"{SITE_URL}/{relative_path}"

                    # Encode URL (if needed)
                    link = encode_url(link)

                    pub_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

                    item = ET.SubElement(channel, "item")
                    ET.SubElement(item, "title").text = title
                    ET.SubElement(item, "link").text = link
                    ET.SubElement(item, "description").text = description
                    ET.SubElement(item, "pubDate").text = pub_date
                    guid = ET.SubElement(item, "guid")
                    guid.text = link
                    guid.set("isPermaLink", "true")

                    if thumbnail_url:
                        media_thumbnail = ET.SubElement(item, "{http://search.yahoo.com/mrss/}thumbnail")
                        media_thumbnail.set("url", thumbnail_url)

                    # Mark this item as processed
                    new_items.add(relative_path)

    # Check if there are new items
    if not new_items:
        print("No new items to add to the RSS feed.")
        return

    # Convert to string and add the XSLT directive
    rss_tree = ET.ElementTree(rss)
    rss_string = ET.tostring(rss, encoding="unicode")
    xslt_directive = f'<?xml-stylesheet type="text/xsl" href="{XSLT_FILE}"?>\n'

    # Debug: Print RSS string before writing
    print("Generated RSS string:")
    print(rss_string)

    # Write the feed with the XSLT directive
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(xslt_directive)
            file.write(rss_string)
        print(f"RSS feed generated: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing feed.xml: {e}")

    # Update the tracker
    processed_items.update(new_items)
    save_processed_items(processed_items)

# Run the script
if __name__ == "__main__":
    generate_rss()

    
TRACKER_FILE = "processed_files.txt"  # File to track processed items

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
                    link = f"{SITE_URL}/{relative_path.replace(os.sep, '/')}"
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

    # Update the tracker
    processed_items.update(new_items)
    save_processed_items(processed_items)

# Run the script
if __name__ == "__main__":
    generate_rss()

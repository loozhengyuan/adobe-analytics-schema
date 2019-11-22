import datetime
import json
import logging
import re

import requests
from bs4 import BeautifulSoup

# Create logger object
logger = logging.getLogger(__name__)


def scrape_column_reference(url="https://docs.adobe.com/content/help/en/analytics/export/analytics-data-feed/data-feed-contents/datafeeds-reference.html", filename="data/column_reference.json"):
    """Helper function for scraping schema data"""

    # Fetch URL
    logger.info(f"Fetching schema from url: {url}")
    s = requests.Session()
    r = s.get(url)

    # Check for error in response
    if r.status_code != 200:
        logger.error(f"Failed to fetch schema: HTTP {r.status_code}")

    # Parse HTML response
    logger.info("Parsing HTML response")
    soup = BeautifulSoup(r.text, features="lxml")

    # Extract schema data
    logger.info("Extracting schema data")
    schema = []
    rows = soup.find("table").find("tbody").find_all("tr")
    for row in rows:
        cells = [e.text.strip() for e in row.find_all("td")]
        schema.append(cells)

    # Format schema
    logger.info("Creating schema meta fields")
    definition = {
        "description": "Column fields for Adobe Analytics (Internal Use)",
        "url": url,
        "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "fields": [],
    }
    logger.info("Appending schema fields to schema dict")
    for element in schema:
        definition["fields"].append(
            {
                "name": element[0],
                "description": element[1],
                "type": element[2],
            }
        )

    # Write to file
    logger.info("Dumping schema dict to JSON file")
    with open(filename, "x") as f:
        json.dump(definition, f)


def _get_sanitised_string(string: str) -> str:
    """
    Returns a sanitised string that matches the
    `[A-Za-z_][A-Za-z0-9_]*` regex pattern

    Args:
        string (str): String to be sanitised

    Reference:
        https://cloud.google.com/bigquery/docs/schemas#column_names
        http://avro.apache.org/docs/current/spec.html#names
    """

    # Check max length
    if len(string) > 128:
        logger.error(f"Tried to sanitise {string} but it has >128 characters")
        return

    # Check reserved names
    reserved_names = (
        "_TABLE_",
        "_FILE_",
        "_PARTITION_",
    )
    if string in reserved_names:
        logger.error(f"Tried to sanitise {string} but it matches one of BigQuery's reserved column names: {reserved_names}")
        return

    # Sanitised
    sanitised = re.sub(r'\W', '_', string)

    # Check if sanitised string starts with illegal character
    if not re.match(r'[a-zA-Z_]', sanitised[0]):
        logger.error(f"Sanitised {string} to {sanitised} but it should start with a letter or an underscore")
        return

    return sanitised

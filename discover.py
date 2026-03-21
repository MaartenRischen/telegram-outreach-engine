import re
import time
import random
import logging
import requests
from bs4 import BeautifulSoup

import config
import db

logger = logging.getLogger(__name__)


def _get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(config.USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return session


def _delay(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))


def _extract_usernames_from_text(text):
    """Extract @usernames and t.me/username links from text."""
    patterns = [
        r"@([a-zA-Z][a-zA-Z0-9_]{4,31})",
        r"t\.me/([a-zA-Z][a-zA-Z0-9_]{4,31})",
    ]
    usernames = set()
    for pattern in patterns:
        for match in re.findall(pattern, text):
            username = match.lower()
            # Filter out common non-channel usernames
            if username not in ("username", "channel", "admin", "bot", "group", "chat"):
                usernames.add(username)
    return usernames


def discover_tgstat(category="technology", country=None, max_pages=3):
    """Discover channels from tgstat.com category pages."""
    session = _get_session()
    found = []

    base_url = "https://tgstat.com"
    if country:
        base_url = f"https://tgstat.com/{country}"

    category_slugs = {
        "technology": "technology",
        "tech": "technology",
        "science": "science",
        "ai": "artificial-intelligence",
        "education": "education",
        "it": "it",
        "crypto": "cryptocurrency",
    }
    slug = category_slugs.get(category.lower(), category.lower())

    channels_found = 0
    for page in range(1, max_pages + 1):
        url = f"{base_url}/ratings/channels/{slug}"
        if page > 1:
            url += f"?page={page}"

        logger.info(f"Fetching tgstat: {url}")
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"tgstat returned {resp.status_code} for {url}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")

            # tgstat channel listings typically have links to t.me or channel pages
            channel_links = soup.select("a[href*='/channel/']")
            if not channel_links:
                # Try alternative selectors
                channel_links = soup.select("a[href*='t.me/']")

            for link in channel_links:
                href = link.get("href", "")
                # Extract username from href
                username = None
                if "/channel/@" in href:
                    username = href.split("/channel/@")[-1].split("/")[0].split("?")[0]
                elif "t.me/" in href:
                    username = href.split("t.me/")[-1].split("/")[0].split("?")[0]
                elif "/channel/" in href:
                    username = href.split("/channel/")[-1].split("/")[0].split("?")[0]

                if username and len(username) >= 5:
                    username = username.lower().lstrip("@")
                    tgstat_url = href if href.startswith("http") else f"{base_url}{href}"

                    # Try to get subscriber count from surrounding text
                    parent = link.find_parent("div") or link.find_parent("tr")
                    sub_count = None
                    if parent:
                        text = parent.get_text()
                        sub_match = re.search(r"([\d,.\s]+)\s*(?:subscribers|подписчик)", text, re.IGNORECASE)
                        if sub_match:
                            sub_count = int(re.sub(r"[,.\s]", "", sub_match.group(1)))

                    channel_id, is_new = db.upsert_channel(
                        username, "tgstat", tgstat_url=tgstat_url
                    )
                    if is_new:
                        channels_found += 1
                        found.append(username)
                        logger.info(f"  Discovered: @{username}")

            if not channel_links:
                logger.info(f"  No channels found on page {page}, stopping")
                break

        except requests.RequestException as e:
            logger.error(f"Error fetching tgstat: {e}")
            break

        _delay(config.TGSTAT_DELAY_MIN, config.TGSTAT_DELAY_MAX)

    db.log_discovery_run("tgstat", category, country, channels_found)
    logger.info(f"tgstat discovery: {channels_found} new channels from '{category}'")
    return found


def discover_telemetr(category="technology", max_pages=3):
    """Discover channels from telemetr.io channel listings."""
    session = _get_session()
    found = []

    category_slugs = {
        "technology": "technologies",
        "tech": "technologies",
        "science": "science",
        "ai": "technologies",
        "education": "education",
        "it": "technologies",
    }
    slug = category_slugs.get(category.lower(), category.lower())

    channels_found = 0
    for page in range(1, max_pages + 1):
        url = f"https://telemetr.io/en/channels?category={slug}"
        if page > 1:
            url += f"&page={page}"

        logger.info(f"Fetching telemetr: {url}")
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"telemetr returned {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")

            # telemetr uses links to t.me channels
            for link in soup.select("a[href*='t.me/']"):
                href = link.get("href", "")
                username = href.split("t.me/")[-1].split("/")[0].split("?")[0]
                if username and len(username) >= 5:
                    username = username.lower()
                    channel_id, is_new = db.upsert_channel(username, "telemetr")
                    if is_new:
                        channels_found += 1
                        found.append(username)
                        logger.info(f"  Discovered: @{username}")

        except requests.RequestException as e:
            logger.error(f"Error fetching telemetr: {e}")
            break

        _delay(config.TELEMETR_DELAY_MIN, config.TELEMETR_DELAY_MAX)

    db.log_discovery_run("telemetr", category, None, channels_found)
    logger.info(f"telemetr discovery: {channels_found} new channels from '{category}'")
    return found


def discover_cross_references(channel_username):
    """Find channels referenced in a channel's posts and description."""
    channel = db.get_channel(channel_username)
    if not channel:
        logger.warning(f"Channel @{channel_username} not found in DB")
        return []

    found = []
    text_to_search = (channel.get("description") or "") + " "

    # Parse sample posts
    sample_posts = channel.get("sample_posts")
    if sample_posts:
        try:
            posts = json.loads(sample_posts) if isinstance(sample_posts, str) else sample_posts
            for post in posts:
                text_to_search += (post.get("text") or "") + " "
        except (json.JSONDecodeError, TypeError):
            pass

    usernames = _extract_usernames_from_text(text_to_search)
    # Remove the channel itself
    usernames.discard(channel_username.lstrip("@").lower())

    for username in usernames:
        channel_id, is_new = db.upsert_channel(username, "cross-reference")
        if is_new:
            found.append(username)
            logger.info(f"  Cross-reference: @{username} from @{channel_username}")

    return found


def add_channels_manually(usernames):
    """Add channels manually by username."""
    added = []
    for username in usernames:
        username = username.lstrip("@").lower()
        if len(username) < 5:
            logger.warning(f"Skipping '{username}' - too short")
            continue
        channel_id, is_new = db.upsert_channel(username, "manual")
        if is_new:
            added.append(username)
            logger.info(f"Added: @{username}")
        else:
            logger.info(f"Already exists: @{username}")
    if added:
        db.log_discovery_run("manual", ",".join(added), None, len(added))
    return added


# Need json for cross_references
import json

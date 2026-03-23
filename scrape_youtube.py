"""YouTube channel scraper using public page meta tags."""

import re
import json
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
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return session


def _delay():
    time.sleep(random.uniform(config.YOUTUBE_DELAY_MIN, config.YOUTUBE_DELAY_MAX))


def scrape_youtube_channel(handle):
    """Scrape a YouTube channel using public page."""
    handle = handle.lstrip("@").strip()
    url = f"https://www.youtube.com/@{handle}"
    session = _get_session()

    logger.info(f"Scraping YouTube: @{handle}")
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"YouTube returned {resp.status_code} for @{handle}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract from meta tags
        title = None
        description = None
        subscriber_count = None
        admin_contact = None

        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            description = og_desc.get("content", "")

        # Subscriber count from meta or page content
        # YouTube embeds channel data in ytInitialData script
        for script in soup.select("script"):
            text = script.string or ""
            if "subscriberCountText" in text:
                match = re.search(r'"subscriberCountText":\{"simpleText":"([\d.]+[KMB]?) subscribers"\}', text)
                if match:
                    count_str = match.group(1)
                    if count_str.endswith("K"):
                        subscriber_count = int(float(count_str[:-1]) * 1000)
                    elif count_str.endswith("M"):
                        subscriber_count = int(float(count_str[:-1]) * 1000000)
                    elif count_str.endswith("B"):
                        subscriber_count = int(float(count_str[:-1]) * 1000000000)
                    else:
                        subscriber_count = int(float(count_str))

            # Look for email in channel about data
            if "businessEmailLabel" in text or "primaryLink" in text:
                emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
                if emails:
                    admin_contact = emails[0]

            # Look for linked social handles
            if "channelExternalLinkViewModel" in text:
                # Find Twitter/X handles
                x_match = re.search(r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)', text)
                ig_match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', text)
                tg_match = re.search(r't\.me/([a-zA-Z0-9_]+)', text)
                if tg_match:
                    admin_contact = (admin_contact or "") + f" tg:@{tg_match.group(1)}"
                if x_match:
                    admin_contact = (admin_contact or "") + f" x:@{x_match.group(1)}"

        if not title:
            logger.warning(f"No data for YouTube @{handle}")
            return None

        handle_lower = handle.lower()
        profile_url = f"https://youtube.com/@{handle}"
        # DM URL: link to about page since YouTube has no DMs
        dm_url = f"https://youtube.com/@{handle}/about"

        db.update_channel(
            handle_lower,
            platform="youtube",
            title=title,
            description=description,
            subscriber_count=subscriber_count,
            admin_contact=admin_contact,
            profile_url=profile_url,
            dm_url=dm_url,
            status="scraped",
        )

        logger.info(f"  Scraped YouTube @{handle}: {title} | {subscriber_count} subs | contact: {admin_contact}")
        return {
            "username": handle_lower,
            "title": title,
            "subscriber_count": subscriber_count,
            "language": "en",
            "admin_contact": admin_contact,
        }

    except requests.RequestException as e:
        logger.error(f"Error scraping YouTube @{handle}: {e}")
        return None


def add_youtube_channels(handles):
    """Add YouTube channels manually."""
    added = []
    for handle in handles:
        handle = handle.lstrip("@").lower()
        channel_id, is_new = db.upsert_channel(handle, "manual", platform="youtube")
        if is_new:
            added.append(handle)
            logger.info(f"Added YouTube: @{handle}")
    return added


def scrape_youtube_channels(limit=None):
    """Scrape all discovered YouTube channels."""
    channels = db.get_channels(status="discovered", platform="youtube")
    if limit:
        channels = channels[:limit]

    results = []
    for i, ch in enumerate(channels):
        handle = ch.get("username") or ch["telegram_username"]
        logger.info(f"[{i+1}/{len(channels)}] Scraping YouTube @{handle}...")
        result = scrape_youtube_channel(handle)
        if result:
            results.append(result)
        if i < len(channels) - 1:
            _delay()

    return results

"""Instagram profile scraper using public meta tags."""

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
    time.sleep(random.uniform(config.INSTAGRAM_DELAY_MIN, config.INSTAGRAM_DELAY_MAX))


def scrape_instagram_profile(username):
    """Scrape an Instagram profile using public page meta tags."""
    username = username.lstrip("@").lower()
    url = f"https://www.instagram.com/{username}/"
    session = _get_session()

    logger.info(f"Scraping Instagram: {username}")
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"Instagram returned {resp.status_code} for @{username}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract from meta tags
        title = None
        description = None
        subscriber_count = None

        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            desc_text = og_desc.get("content", "")
            description = desc_text

            # Parse follower count from og:description
            # Format: "1.2M Followers, 500 Following, 200 Posts - ..."
            # or "1,234 Followers"
            follower_match = re.search(r"([\d,.]+[KMB]?)\s*Followers", desc_text, re.IGNORECASE)
            if follower_match:
                count_str = follower_match.group(1).replace(",", "")
                if count_str.endswith("K"):
                    subscriber_count = int(float(count_str[:-1]) * 1000)
                elif count_str.endswith("M"):
                    subscriber_count = int(float(count_str[:-1]) * 1000000)
                elif count_str.endswith("B"):
                    subscriber_count = int(float(count_str[:-1]) * 1000000000)
                else:
                    subscriber_count = int(float(count_str))

        # Try to get bio from page description meta
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and not description:
            description = meta_desc.get("content", "")

        # Try JSON-LD
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") == "ProfilePage":
                        title = title or data.get("name", "")
                        description = description or data.get("description", "")
                        if "interactionStatistic" in data:
                            for stat in data["interactionStatistic"]:
                                if "Follow" in str(stat.get("interactionType", "")):
                                    subscriber_count = subscriber_count or int(stat.get("userInteractionCount", 0))
            except (json.JSONDecodeError, TypeError):
                pass

        if not title and not description:
            logger.warning(f"No data for Instagram @{username} - may need login")
            return None

        profile_url = f"https://instagram.com/{username}"
        dm_url = f"https://instagram.com/{username}"

        db.update_channel(
            username,
            platform="instagram",
            title=title,
            description=description,
            subscriber_count=subscriber_count,
            profile_url=profile_url,
            dm_url=dm_url,
            status="scraped",
        )

        logger.info(f"  Scraped Instagram @{username}: {title} | {subscriber_count} followers")
        return {
            "username": username,
            "title": title,
            "subscriber_count": subscriber_count,
            "language": "en",
        }

    except requests.RequestException as e:
        logger.error(f"Error scraping Instagram @{username}: {e}")
        return None


def add_instagram_profiles(usernames):
    """Add Instagram profiles manually."""
    added = []
    for username in usernames:
        username = username.lstrip("@").lower()
        channel_id, is_new = db.upsert_channel(username, "manual", platform="instagram")
        if is_new:
            added.append(username)
            logger.info(f"Added Instagram: @{username}")
    return added


def scrape_instagram_channels(limit=None):
    """Scrape all discovered Instagram profiles."""
    channels = db.get_channels(status="discovered", platform="instagram")
    if limit:
        channels = channels[:limit]

    results = []
    for i, ch in enumerate(channels):
        username = ch.get("username") or ch["telegram_username"]
        logger.info(f"[{i+1}/{len(channels)}] Scraping Instagram @{username}...")
        result = scrape_instagram_profile(username)
        if result:
            results.append(result)
        if i < len(channels) - 1:
            _delay()

    return results

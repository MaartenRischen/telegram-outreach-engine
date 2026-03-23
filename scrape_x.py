"""X/Twitter profile scraper using syndication endpoint."""

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
    time.sleep(random.uniform(config.X_DELAY_MIN, config.X_DELAY_MAX))


def scrape_x_profile(username):
    """Scrape an X/Twitter profile using the syndication endpoint."""
    username = username.lstrip("@").strip()
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    session = _get_session()

    logger.info(f"Scraping X: @{username}")
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"X syndication returned {resp.status_code} for @{username}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # The syndication page contains timeline tweets and profile info
        title = None
        description = None
        subscriber_count = None

        # Look for profile header info
        header = soup.select_one(".timeline-Header-title")
        if header:
            title = header.get_text(strip=True)

        bio = soup.select_one(".timeline-Header-description")
        if bio:
            description = bio.get_text(strip=True)

        # Extract recent tweets for sample_posts
        tweets = []
        for tweet_el in soup.select(".timeline-Tweet-text"):
            text = tweet_el.get_text(strip=True)
            if text:
                tweets.append({"text": text[:500]})

        # Try to get follower count from profile if available
        for meta in soup.select("meta"):
            content = meta.get("content", "")
            if "followers" in content.lower():
                match = re.search(r"([\d,.]+[KMB]?)\s*(?:Followers|followers)", content)
                if match:
                    count_str = match.group(1).replace(",", "")
                    if count_str.endswith("K"):
                        subscriber_count = int(float(count_str[:-1]) * 1000)
                    elif count_str.endswith("M"):
                        subscriber_count = int(float(count_str[:-1]) * 1000000)
                    else:
                        try:
                            subscriber_count = int(count_str)
                        except ValueError:
                            pass

        if not title and not tweets:
            # Fallback: try the regular x.com page meta tags
            logger.info(f"  Syndication empty, trying x.com meta tags for @{username}")
            resp2 = session.get(f"https://x.com/{username}", timeout=15)
            soup2 = BeautifulSoup(resp2.text, "html.parser")

            og_title = soup2.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "")

            og_desc = soup2.find("meta", property="og:description")
            if og_desc:
                description = og_desc.get("content", "")
                # Parse follower count from description
                match = re.search(r"([\d,.]+[KMB]?)\s*Followers", description)
                if match:
                    count_str = match.group(1).replace(",", "")
                    if count_str.endswith("K"):
                        subscriber_count = int(float(count_str[:-1]) * 1000)
                    elif count_str.endswith("M"):
                        subscriber_count = int(float(count_str[:-1]) * 1000000)
                    else:
                        try:
                            subscriber_count = int(count_str)
                        except ValueError:
                            pass

        if not title and not description:
            logger.warning(f"No data for X @{username}")
            return None

        username_lower = username.lower()
        profile_url = f"https://x.com/{username}"
        dm_url = f"https://x.com/{username}"

        sample_posts_json = json.dumps(tweets[:10], ensure_ascii=False) if tweets else None

        db.update_channel(
            username_lower,
            platform="x",
            title=title,
            description=description,
            subscriber_count=subscriber_count,
            sample_posts=sample_posts_json,
            profile_url=profile_url,
            dm_url=dm_url,
            status="scraped",
        )

        logger.info(f"  Scraped X @{username}: {title} | {subscriber_count} followers | {len(tweets)} tweets")
        return {
            "username": username_lower,
            "title": title,
            "subscriber_count": subscriber_count,
            "language": "en",
        }

    except requests.RequestException as e:
        logger.error(f"Error scraping X @{username}: {e}")
        return None


def add_x_profiles(usernames):
    """Add X/Twitter profiles manually."""
    added = []
    for username in usernames:
        username = username.lstrip("@").lower()
        channel_id, is_new = db.upsert_channel(username, "manual", platform="x")
        if is_new:
            added.append(username)
            logger.info(f"Added X: @{username}")
    return added


def scrape_x_channels(limit=None):
    """Scrape all discovered X profiles."""
    channels = db.get_channels(status="discovered", platform="x")
    if limit:
        channels = channels[:limit]

    results = []
    for i, ch in enumerate(channels):
        username = ch.get("username") or ch["telegram_username"]
        logger.info(f"[{i+1}/{len(channels)}] Scraping X @{username}...")
        result = scrape_x_profile(username)
        if result:
            results.append(result)
        if i < len(channels) - 1:
            _delay()

    return results

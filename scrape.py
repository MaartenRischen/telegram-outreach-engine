import re
import json
import time
import random
import logging
import unicodedata
import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

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
    time.sleep(random.uniform(config.TELEGRAM_WEB_DELAY_MIN, config.TELEGRAM_WEB_DELAY_MAX))


def _detect_script(text):
    """Detect the dominant script in text."""
    scripts = {}
    for char in text:
        if char.isalpha():
            try:
                script = unicodedata.name(char).split()[0]
            except ValueError:
                continue
            scripts[script] = scripts.get(script, 0) + 1
    if not scripts:
        return None
    return max(scripts, key=scripts.get)


def detect_language(text):
    """Detect language from text with script-based fallbacks."""
    if not text or len(text.strip()) < 20:
        return None

    # Script-based heuristics first for non-Latin scripts
    dominant_script = _detect_script(text)

    if dominant_script == "CYRILLIC":
        # Check for Ukrainian-specific letters
        ukr_chars = set("іїєґ")
        if any(c in text.lower() for c in ukr_chars):
            return "uk"
        return "ru"

    if dominant_script in ("CJK", "IDEOGRAPH"):
        # Check for Japanese kana
        if any("\u3040" <= c <= "\u309F" or "\u30A0" <= c <= "\u30FF" for c in text):
            return "ja"
        # Check for Korean jamo/syllables
        if any("\uAC00" <= c <= "\uD7AF" or "\u1100" <= c <= "\u11FF" for c in text):
            return "ko"
        return "zh"

    if dominant_script == "ARABIC":
        return "ar"
    if dominant_script == "DEVANAGARI":
        return "hi"
    if dominant_script == "THAI":
        return "th"

    # Fallback to langdetect for Latin and other scripts
    try:
        return detect(text)
    except LangDetectException:
        return None


def _extract_admin(description):
    """Extract admin username from channel description."""
    if not description:
        return None, None

    admin_username = None
    admin_contact = None

    # Common patterns for admin username
    admin_patterns = [
        r"(?:admin|админ|contact|связь|по\s+вопросам|owner|founder|автор|обратная\s+связь|реклама|advertising|cooperation)\s*[:\-–—\s]\s*@([a-zA-Z][a-zA-Z0-9_]{4,31})",
        r"(?:для\s+связи|for\s+contact)\s*[:\-–—\s]*@([a-zA-Z][a-zA-Z0-9_]{4,31})",
        r"@([a-zA-Z][a-zA-Z0-9_]{4,31})\s*(?:\-\s*)?(?:admin|админ|owner|founder|автор)",
    ]
    for pattern in admin_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            admin_username = match.group(1)
            break

    # If no admin pattern found, look for any @username in description
    if not admin_username:
        usernames = re.findall(r"@([a-zA-Z][a-zA-Z0-9_]{4,31})", description)
        # Filter out bot usernames
        usernames = [u for u in usernames if not u.lower().endswith("bot")]
        if len(usernames) == 1:
            admin_username = usernames[0]

    # Look for email
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", description)
    if email_match:
        admin_contact = email_match.group(0)

    return admin_username, admin_contact


def _classify_tone(posts_text):
    """Classify channel tone based on post content."""
    if not posts_text:
        return "unknown"

    emoji_count = sum(1 for c in posts_text if ord(c) > 0x1F600)
    word_count = len(posts_text.split())
    if word_count == 0:
        return "unknown"

    emoji_ratio = emoji_count / word_count

    # Check for technical indicators
    tech_patterns = [
        r"\b(?:API|SDK|GPU|CPU|LLM|NLP|GPT|BERT|transformer|neural|model|algorithm|benchmark|dataset)\b",
        r"```",
        r"\b(?:import|def|class|function|return|const|var|let)\b",
    ]
    tech_score = sum(
        len(re.findall(p, posts_text, re.IGNORECASE)) for p in tech_patterns
    )

    if tech_score > 10:
        return "technical"
    if emoji_ratio > 0.05:
        return "meme-heavy"
    if any(
        word in posts_text.lower()
        for word in ["уважаемые", "dear", "please note", "hereby", "furthermore"]
    ):
        return "formal"
    return "casual"


def _estimate_post_frequency(dates):
    """Estimate posting frequency from a list of post dates."""
    if not dates or len(dates) < 2:
        return "unknown"

    from datetime import datetime

    parsed = []
    for d in dates:
        if isinstance(d, str):
            for fmt in ("%Y-%m-%d", "%B %d", "%b %d", "%d %B", "%d %b"):
                try:
                    parsed.append(datetime.strptime(d, fmt))
                    break
                except ValueError:
                    continue

    if len(parsed) < 2:
        return "unknown"

    parsed.sort()
    gaps = [(parsed[i + 1] - parsed[i]).days for i in range(len(parsed) - 1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    if avg_gap <= 1.5:
        return "daily"
    if avg_gap <= 4:
        return "several-per-week"
    if avg_gap <= 8:
        return "weekly"
    return "sporadic"


def scrape_telegram_channel(username):
    """Scrape a channel's public web preview at t.me/s/username."""
    username = username.lstrip("@").lower()
    url = f"https://t.me/s/{username}"
    session = _get_session()

    logger.info(f"Scraping t.me/s/{username}")
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"t.me returned {resp.status_code} for @{username}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Channel info
        title_el = soup.select_one(".tgme_channel_info_header_title")
        title = title_el.get_text(strip=True) if title_el else None

        desc_el = soup.select_one(".tgme_channel_info_description")
        description = desc_el.get_text(strip=True) if desc_el else None

        # Subscriber count
        sub_el = soup.select_one(".tgme_channel_info_counter .counter_value")
        subscriber_count = None
        if sub_el:
            sub_text = sub_el.get_text(strip=True).replace(" ", "").replace("\xa0", "")
            # Handle K/M suffixes
            if sub_text.endswith("K"):
                subscriber_count = int(float(sub_text[:-1]) * 1000)
            elif sub_text.endswith("M"):
                subscriber_count = int(float(sub_text[:-1]) * 1000000)
            else:
                try:
                    subscriber_count = int(sub_text)
                except ValueError:
                    pass

        # Posts
        posts = []
        post_elements = soup.select(".tgme_widget_message_wrap")
        all_text = ""
        post_dates = []

        for post_el in post_elements:
            post_data = {}

            # Post text
            text_el = post_el.select_one(".tgme_widget_message_text")
            if text_el:
                post_data["text"] = text_el.get_text(strip=True)
                all_text += post_data["text"] + " "

            # Views
            views_el = post_el.select_one(".tgme_widget_message_views")
            if views_el:
                views_text = views_el.get_text(strip=True).replace(" ", "")
                if views_text.endswith("K"):
                    post_data["views"] = int(float(views_text[:-1]) * 1000)
                elif views_text.endswith("M"):
                    post_data["views"] = int(float(views_text[:-1]) * 1000000)
                else:
                    try:
                        post_data["views"] = int(views_text)
                    except ValueError:
                        pass

            # Date
            date_el = post_el.select_one(".tgme_widget_message_date time")
            if date_el:
                post_data["date"] = date_el.get("datetime", "")[:10]
                post_dates.append(post_data["date"])

            # Reactions (if available in the HTML)
            reactions = {}
            reaction_els = post_el.select(".tgme_widget_message_reaction")
            for react_el in reaction_els:
                emoji_el = react_el.select_one(".reaction_emoji, .emoji")
                count_el = react_el.select_one(".reaction_count, .counter")
                if emoji_el and count_el:
                    emoji = emoji_el.get_text(strip=True)
                    try:
                        count = int(count_el.get_text(strip=True).replace(",", ""))
                        reactions[emoji] = count
                    except ValueError:
                        pass
            if reactions:
                post_data["reactions"] = reactions

            if post_data.get("text"):
                posts.append(post_data)

        if not title and not posts:
            logger.warning(f"No data found for @{username} - channel may be private or not exist")
            return None

        # Calculate metrics
        views = [p["views"] for p in posts if "views" in p]
        avg_views = int(sum(views) / len(views)) if views else None

        total_reactions = []
        for p in posts:
            if "reactions" in p:
                total_reactions.append(sum(p["reactions"].values()))
        avg_reactions = int(sum(total_reactions) / len(total_reactions)) if total_reactions else None

        reaction_ratio = None
        if avg_views and avg_reactions and avg_views > 0:
            reaction_ratio = round(avg_reactions / avg_views, 4)

        # Language detection
        language = detect_language(all_text)

        # Admin extraction
        admin_username, admin_contact = _extract_admin(description)

        # Tone classification
        tone = _classify_tone(all_text)

        # Post frequency
        post_frequency = _estimate_post_frequency(post_dates)

        # Topic detection (simple keyword-based)
        topics = _detect_topics(all_text)

        # Store sample posts (last 20, with truncated text)
        sample_posts = []
        for p in posts[:20]:
            sample = {"text": p.get("text", "")[:500]}
            if "views" in p:
                sample["views"] = p["views"]
            if "reactions" in p:
                sample["reactions"] = p["reactions"]
            if "date" in p:
                sample["date"] = p["date"]
            sample_posts.append(sample)

        # Update DB
        db.update_channel(
            username,
            title=title,
            description=description,
            subscriber_count=subscriber_count,
            language=language,
            avg_post_views=avg_views,
            avg_reactions=avg_reactions,
            reaction_view_ratio=reaction_ratio,
            post_frequency=post_frequency,
            admin_username=admin_username,
            admin_contact=admin_contact,
            topics=json.dumps(topics),
            tone=tone,
            sample_posts=json.dumps(sample_posts, ensure_ascii=False),
            status="scraped",
        )

        logger.info(
            f"  Scraped @{username}: {title} | {subscriber_count} subs | {language} | {len(posts)} posts"
        )
        return {
            "username": username,
            "title": title,
            "subscriber_count": subscriber_count,
            "language": language,
            "posts_scraped": len(posts),
        }

    except requests.RequestException as e:
        logger.error(f"Error scraping @{username}: {e}")
        return None


def _detect_topics(text):
    """Detect topics from post text using keyword matching."""
    if not text:
        return []

    topic_keywords = {
        "AI/ML": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural network",
                   "llm", "gpt", "chatgpt", "claude", "gemini", "нейросет", "искусственн", "ии"],
        "Programming": ["programming", "coding", "developer", "python", "javascript", "code", "github",
                        "программирован", "разработк"],
        "Data Science": ["data science", "analytics", "data analysis", "big data", "данны"],
        "NLP": ["nlp", "natural language", "text generation", "language model", "обработк.*текст"],
        "Computer Vision": ["computer vision", "image recognition", "image generation", "midjourney",
                           "stable diffusion", "dall-e", "генераци.*изображ"],
        "Robotics": ["robotics", "automation", "robot", "робот", "автоматизац"],
        "Crypto/Web3": ["crypto", "blockchain", "web3", "nft", "defi", "крипто", "блокчейн"],
        "Startups": ["startup", "founder", "venture", "fundraising", "стартап"],
        "Science": ["research", "paper", "arxiv", "study", "experiment", "исследован", "наук"],
        "Education": ["tutorial", "course", "learn", "education", "обучен", "курс", "урок"],
        "Productivity": ["productivity", "tool", "app", "workflow", "продуктивност", "инструмент"],
        "Hardware": ["gpu", "chip", "hardware", "nvidia", "amd", "intel", "железо"],
    }

    text_lower = text.lower()
    detected = []
    for topic, keywords in topic_keywords.items():
        for kw in keywords:
            if re.search(kw, text_lower):
                detected.append(topic)
                break

    return detected


def scrape_channels(limit=None, status="discovered", channel_username=None):
    """Scrape multiple channels. Returns list of results."""
    if channel_username:
        channels = [db.get_channel(channel_username)]
        channels = [c for c in channels if c]
    else:
        channels = db.get_channels(status=status)

    if limit:
        channels = channels[:limit]

    results = []
    for i, channel in enumerate(channels):
        username = channel["telegram_username"]
        logger.info(f"[{i+1}/{len(channels)}] Scraping @{username}...")
        result = scrape_telegram_channel(username)
        if result:
            results.append(result)
        if i < len(channels) - 1:
            _delay()

    return results

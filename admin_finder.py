"""
Find and fill missing admin usernames for scraped channels ready for messages.
Scrapes t.me/s/{username} for @mentions in description and posts.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
import requests
import re
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def has_real_admin(channel):
    """Check if a channel has a real admin_username (not empty, not same as channel username)."""
    admin = channel.get("admin_username")
    if not admin or not admin.strip():
        return False
    # Admin shouldn't be the same as the channel username
    if admin.strip().lower() == channel["telegram_username"].strip().lower():
        return False
    return True


def scrape_admin_from_web(username):
    """Scrape t.me/s/{username} and look for @mentions that could be admin handles."""
    url = f"https://t.me/s/{username}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"    HTTP {resp.status_code} for t.me/s/{username}")
            return None
    except requests.RequestException as e:
        print(f"    Request error for @{username}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Gather all text to search for @mentions
    mentions_found = []

    # 1. Check channel description
    desc_el = soup.select_one(".tgme_channel_info_description")
    if desc_el:
        desc_text = desc_el.get_text(separator=" ", strip=True)
        desc_html = str(desc_el)

        # Look for admin-related patterns first (highest priority)
        admin_patterns = [
            r"(?:admin|админ|contact|связь|по\s+вопросам|owner|founder|обратная\s+связь|сотрудничество|cooperation)\s*[:\-–—\s]\s*@([a-zA-Z][a-zA-Z0-9_]{4,31})",
            r"(?:для\s+связи|for\s+contact|по\s+рекламе|реклама)\s*[:\-–—\s]*@([a-zA-Z][a-zA-Z0-9_]{4,31})",
            r"(?:автор|author|created\s+by)\s*[:\-–—\s]*@([a-zA-Z][a-zA-Z0-9_]{4,31})",
            r"@([a-zA-Z][a-zA-Z0-9_]{4,31})\s*(?:\-\s*)?(?:admin|админ|owner|founder|автор)",
            r"(?:PR|пр)\s*[:\-–—\s]*@([a-zA-Z][a-zA-Z0-9_]{4,31})",
        ]

        normalized_desc = re.sub(r'([^\s])@', r'\1 @', desc_text)
        for pattern in admin_patterns:
            match = re.search(pattern, normalized_desc, re.IGNORECASE)
            if match:
                handle = match.group(1)
                if handle.lower() != username.lower() and not handle.lower().endswith("bot"):
                    return handle  # High-confidence match

        # Fallback: any @mentions in description
        desc_mentions = re.findall(r"@([a-zA-Z][a-zA-Z0-9_]{4,31})", normalized_desc)
        for m in desc_mentions:
            if m.lower() != username.lower() and not m.lower().endswith("bot") and not m.lower().endswith("_channel"):
                mentions_found.append(("desc", m))

    # 2. Check posts for @mentions (lower priority)
    post_elements = soup.select(".tgme_widget_message_text")
    post_mentions = {}
    for post_el in post_elements:
        post_text = post_el.get_text(separator=" ", strip=True)
        found = re.findall(r"@([a-zA-Z][a-zA-Z0-9_]{4,31})", post_text)
        for m in found:
            if m.lower() != username.lower() and not m.lower().endswith("bot") and not m.lower().endswith("_channel"):
                post_mentions[m] = post_mentions.get(m, 0) + 1

    # Prefer description mentions, then most-mentioned in posts
    if mentions_found:
        return mentions_found[0][1]

    if post_mentions:
        # Return the most frequently mentioned handle
        best = max(post_mentions, key=post_mentions.get)
        if post_mentions[best] >= 2:  # Only if mentioned at least twice
            return best

    return None


def main():
    print("=" * 70)
    print("ADMIN FINDER - Channels Ready for Messages")
    print("=" * 70)

    # Step 1: Get all channels ready for messages
    channels = db.get_channels_ready_for_messages()
    print(f"\nTotal channels with status='scraped' and no messages: {len(channels)}")

    # Step 2: Filter to 1000+ subscribers
    channels = [c for c in channels if (c.get("subscriber_count") or 0) >= 1000]
    print(f"Channels with 1000+ subscribers: {len(channels)}")

    if not channels:
        print("\nNo channels to process.")
        return

    # Step 3 & 4: Check admin status and scrape if missing
    has_admin = []
    missing_admin = []
    scraped_count = 0
    found_count = 0

    for ch in channels:
        if has_real_admin(ch):
            has_admin.append(ch)
        else:
            missing_admin.append(ch)

    print(f"\nChannels with admin: {len(has_admin)}")
    print(f"Channels missing admin: {len(missing_admin)}")
    print()

    if missing_admin:
        print("-" * 70)
        print(f"Scraping t.me for admin handles on {len(missing_admin)} channels...")
        print("-" * 70)

        for i, ch in enumerate(missing_admin):
            username = ch["telegram_username"]
            print(f"\n  [{i+1}/{len(missing_admin)}] @{username} ({ch.get('subscriber_count', '?')} subs)")

            admin_handle = scrape_admin_from_web(username)
            scraped_count += 1

            if admin_handle:
                print(f"    -> Found admin: @{admin_handle}")
                db.update_channel(username, admin_username=admin_handle)
                ch["admin_username"] = admin_handle
                found_count += 1
            else:
                print(f"    -> No admin found")

            # Rate limiting
            if i < len(missing_admin) - 1:
                time.sleep(2)

        print(f"\n\nScraping complete: found {found_count}/{scraped_count} admin handles")

    # Step 5: Refresh data and print summary
    channels = db.get_channels_ready_for_messages()
    channels = [c for c in channels if (c.get("subscriber_count") or 0) >= 1000]

    print("\n" + "=" * 70)
    print("SUMMARY: All Channels Ready for Messages (1000+ subs)")
    print("=" * 70)
    print(f"{'#':<4} {'Username':<25} {'Subs':<10} {'Lang':<6} {'Admin':<25} {'Status'}")
    print("-" * 100)

    ready_with_admin = 0
    ready_no_admin = 0

    for i, ch in enumerate(channels, 1):
        username = ch["telegram_username"]
        subs = ch.get("subscriber_count", "?")
        lang = ch.get("language", "?")
        admin = ch.get("admin_username", "")
        has_adm = has_real_admin(ch)

        if has_adm:
            admin_display = f"@{admin}"
            status = "READY"
            ready_with_admin += 1
        else:
            admin_display = "-"
            status = "NO ADMIN"
            ready_no_admin += 1

        print(f"{i:<4} @{username:<24} {str(subs):<10} {str(lang):<6} {admin_display:<25} {status}")

    print("-" * 100)
    print(f"\nTotal: {len(channels)} channels")
    print(f"  Ready (have admin):  {ready_with_admin}")
    print(f"  No admin found:     {ready_no_admin}")
    print()


if __name__ == "__main__":
    main()

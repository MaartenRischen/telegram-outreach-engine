#!/usr/bin/env python3
"""Telegram Outreach Engine CLI."""

import sys
import json
import csv
import io
import logging
import argparse

import db
import discover
import scrape
from config import DASHBOARD_HOST, DASHBOARD_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def cmd_discover(args):
    """Discover channels from tgstat or telemetr."""
    source = args.source
    category = args.category
    max_pages = args.pages

    if source == "tgstat":
        found = discover.discover_tgstat(category=category, country=args.country, max_pages=max_pages)
    elif source == "telemetr":
        found = discover.discover_telemetr(category=category, max_pages=max_pages)
    else:
        print(f"Unknown source: {source}")
        return

    print(f"\nDiscovered {len(found)} new channels:")
    for u in found:
        print(f"  @{u}")


def cmd_add(args):
    """Manually add channels."""
    usernames = args.channels
    added = discover.add_channels_manually(usernames)
    print(f"\nAdded {len(added)} new channels:")
    for u in added:
        print(f"  @{u}")


def cmd_scrape(args):
    """Scrape channel data."""
    if args.channel:
        results = scrape.scrape_channels(channel_username=args.channel)
    else:
        status = args.status or "discovered"
        results = scrape.scrape_channels(limit=args.limit, status=status)

    print(f"\nScraped {len(results)} channels:")
    for r in results:
        print(f"  @{r['username']}: {r['title']} ({r['subscriber_count']} subs, {r['language']})")


def cmd_ready(args):
    """Show channels ready for message generation."""
    channels = db.get_channels_ready_for_messages(
        language=args.language,
        min_subscribers=args.min_subscribers,
    )

    if not channels:
        print("No channels ready for message generation.")
        print("Run 'python cli.py scrape' first to scrape discovered channels.")
        return

    print(f"\n{'='*80}")
    print(f"CHANNELS READY FOR MESSAGE GENERATION ({len(channels)} total)")
    print(f"{'='*80}\n")

    for ch in channels:
        topics = json.loads(ch["topics"]) if ch.get("topics") else []
        print(f"@{ch['telegram_username']}")
        print(f"  Title:       {ch.get('title', 'N/A')}")
        print(f"  Language:    {ch.get('language', 'N/A')}")
        print(f"  Subscribers: {ch.get('subscriber_count', 'N/A')}")
        print(f"  Avg Views:   {ch.get('avg_post_views', 'N/A')}")
        print(f"  Avg React:   {ch.get('avg_reactions', 'N/A')}")
        print(f"  Ratio:       {ch.get('reaction_view_ratio', 'N/A')}")
        print(f"  Frequency:   {ch.get('post_frequency', 'N/A')}")
        print(f"  Tone:        {ch.get('tone', 'N/A')}")
        print(f"  Topics:      {', '.join(topics) if topics else 'N/A'}")
        print(f"  Admin:       @{ch['admin_username']}" if ch.get("admin_username") else "  Admin:       N/A")
        if ch.get("description"):
            desc = ch["description"][:200] + "..." if len(ch["description"]) > 200 else ch["description"]
            print(f"  Description: {desc}")
        print()


def cmd_show(args):
    """Show detailed channel info."""
    channel = db.get_channel(args.channel)
    if not channel:
        print(f"Channel @{args.channel.lstrip('@')} not found.")
        return

    print(f"\n{'='*80}")
    print(f"CHANNEL: @{channel['telegram_username']}")
    print(f"{'='*80}\n")

    for key, val in channel.items():
        if key in ("sample_posts", "topics") and val:
            try:
                parsed = json.loads(val) if isinstance(val, str) else val
                print(f"{key}:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except (json.JSONDecodeError, TypeError):
                print(f"{key}: {val}")
        else:
            print(f"{key}: {val}")

    # Show messages
    messages = db.get_messages(channel["id"])
    if messages:
        print(f"\n{'='*40}")
        print("MESSAGES:")
        for msg in messages:
            print(f"\n  [{msg['id']}] Created: {msg['created_at']}")
            print(f"  Language: {msg['language']}")
            print(f"  Sent: {msg.get('sent_at', 'No')}")
            print(f"  Text:\n    {msg['message_text']}")
            if msg.get("response_text"):
                print(f"  Response: {msg['response_text']}")


def cmd_message(args):
    """Insert a generated message for a channel."""
    channel = db.get_channel(args.channel)
    if not channel:
        print(f"Channel @{args.channel.lstrip('@')} not found.")
        return

    language = channel.get("language") or "en"
    db.insert_message(args.channel, args.text, language)
    print(f"Message saved for @{args.channel.lstrip('@')} (language: {language})")


def cmd_sent(args):
    """Mark a channel's message as sent."""
    try:
        db.mark_sent(args.channel)
        print(f"Marked @{args.channel.lstrip('@')} as sent.")
    except ValueError as e:
        print(str(e))


def cmd_response(args):
    """Record a response from a channel admin."""
    try:
        db.record_response(args.channel, args.text)
        print(f"Response recorded for @{args.channel.lstrip('@')}.")
    except ValueError as e:
        print(str(e))


def cmd_dashboard(args):
    """Start the web dashboard."""
    from dashboard import app
    print(f"Starting dashboard at http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=True)


def cmd_export(args):
    """Export channels and messages."""
    channels = db.get_channels()
    fmt = args.format

    if fmt == "json":
        for ch in channels:
            ch["messages"] = db.get_messages(ch["id"])
        output = json.dumps(channels, indent=2, ensure_ascii=False, default=str)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Exported to {args.output}")
        else:
            print(output)

    elif fmt == "csv":
        if not channels:
            print("No channels to export.")
            return
        keys = [
            "telegram_username", "title", "language", "subscriber_count",
            "avg_post_views", "avg_reactions", "reaction_view_ratio",
            "post_frequency", "admin_username", "tone", "status",
        ]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(channels)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output.getvalue())
            print(f"Exported to {args.output}")
        else:
            print(output.getvalue())


def cmd_stats(args):
    """Show pipeline statistics."""
    stats = db.get_stats()

    print(f"\n{'='*50}")
    print("TELEGRAM OUTREACH PIPELINE STATS")
    print(f"{'='*50}\n")

    print(f"Total channels: {stats['total_channels']}")
    print()

    print("By status:")
    for status, count in sorted(stats["by_status"].items(), key=lambda x: -x[1]):
        print(f"  {status:20s} {count:5d}")
    print()

    print("By language:")
    for lang, count in stats["by_language"].items():
        print(f"  {lang or 'unknown':20s} {count:5d}")
    print()

    print(f"Total messages:     {stats['total_messages']}")
    print(f"Messages sent:      {stats['messages_sent']}")
    print(f"Responses received: {stats['responses_received']}")
    print(f"Response rate:      {stats['response_rate']}%")


def main():
    parser = argparse.ArgumentParser(description="Telegram Outreach Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # discover
    p_discover = subparsers.add_parser("discover", help="Discover channels")
    p_discover.add_argument("--source", required=True, choices=["tgstat", "telemetr"])
    p_discover.add_argument("--category", default="technology")
    p_discover.add_argument("--country", default=None)
    p_discover.add_argument("--pages", type=int, default=3)
    p_discover.set_defaults(func=cmd_discover)

    # add
    p_add = subparsers.add_parser("add", help="Manually add channels")
    p_add.add_argument("channels", nargs="+")
    p_add.set_defaults(func=cmd_add)

    # scrape
    p_scrape = subparsers.add_parser("scrape", help="Scrape channel data")
    p_scrape.add_argument("--limit", type=int, default=None)
    p_scrape.add_argument("--channel", default=None)
    p_scrape.add_argument("--status", default=None)
    p_scrape.set_defaults(func=cmd_scrape)

    # ready
    p_ready = subparsers.add_parser("ready", help="Show channels ready for messages")
    p_ready.add_argument("--language", default=None)
    p_ready.add_argument("--min-subscribers", type=int, default=None)
    p_ready.set_defaults(func=cmd_ready)

    # show
    p_show = subparsers.add_parser("show", help="Show channel details")
    p_show.add_argument("channel")
    p_show.set_defaults(func=cmd_show)

    # message
    p_msg = subparsers.add_parser("message", help="Insert a generated message")
    p_msg.add_argument("channel")
    p_msg.add_argument("text")
    p_msg.set_defaults(func=cmd_message)

    # sent
    p_sent = subparsers.add_parser("sent", help="Mark message as sent")
    p_sent.add_argument("channel")
    p_sent.set_defaults(func=cmd_sent)

    # response
    p_resp = subparsers.add_parser("response", help="Record a response")
    p_resp.add_argument("channel")
    p_resp.add_argument("text")
    p_resp.set_defaults(func=cmd_response)

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="Start web dashboard")
    p_dash.set_defaults(func=cmd_dashboard)

    # export
    p_export = subparsers.add_parser("export", help="Export data")
    p_export.add_argument("--format", choices=["csv", "json"], default="json")
    p_export.add_argument("--output", "-o", default=None)
    p_export.set_defaults(func=cmd_export)

    # stats
    p_stats = subparsers.add_parser("stats", help="Show pipeline stats")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()

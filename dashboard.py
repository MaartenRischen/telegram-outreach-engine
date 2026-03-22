"""Flask web dashboard for Telegram Outreach Engine."""

import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

import db
import discover
import scrape as scrape_module

app = Flask(__name__)

# Track background jobs
_jobs = {}
_jobs_lock = threading.Lock()


def _run_job(job_id, fn, *args, **kwargs):
    """Run a function in a background thread, tracking status."""
    try:
        result = fn(*args, **kwargs)
        with _jobs_lock:
            _jobs[job_id]["status"] = "done"
            _jobs[job_id]["result"] = result
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = str(e)


def _start_job(job_id, fn, *args, **kwargs):
    with _jobs_lock:
        _jobs[job_id] = {"status": "running", "started": datetime.now().isoformat()}
    t = threading.Thread(target=_run_job, args=(job_id, fn, *args), kwargs=kwargs, daemon=True)
    t.start()


@app.template_filter("fromjson")
def fromjson_filter(value):
    if not value:
        return []
    try:
        return json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return []


@app.template_filter("timeago")
def timeago_filter(value):
    if not value:
        return "N/A"
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value)
        else:
            dt = value
        delta = datetime.now() - dt
        days = delta.days
        if days == 0:
            return "today"
        if days == 1:
            return "yesterday"
        return f"{days} days ago"
    except (ValueError, TypeError):
        return str(value)


@app.route("/")
def index():
    stats = db.get_stats()
    discovery_runs = db.get_discovery_runs()[:10]
    return render_template("discovery.html", stats=stats, discovery_runs=discovery_runs)


@app.route("/channels")
def channels():
    status = request.args.get("status")
    language = request.args.get("language")
    min_subs = request.args.get("min_subscribers", type=int)
    sort = request.args.get("sort", "subscriber_count DESC")

    # Sanitize sort parameter
    allowed_sorts = {
        "subscribers_asc": "subscriber_count ASC",
        "subscribers_desc": "subscriber_count DESC",
        "views_asc": "avg_post_views ASC",
        "views_desc": "avg_post_views DESC",
        "ratio_desc": "reaction_view_ratio DESC",
        "name_asc": "telegram_username ASC",
        "newest": "created_at DESC",
    }
    order = allowed_sorts.get(sort, "subscriber_count DESC")

    channel_list = db.get_channels(status=status, language=language, min_subscribers=min_subs, order_by=order)

    # Get unique languages and statuses for filters
    all_channels = db.get_channels()
    languages = sorted(set(c["language"] for c in all_channels if c.get("language")))
    statuses = sorted(set(c["status"] for c in all_channels if c.get("status")))

    return render_template(
        "channels.html",
        channels=channel_list,
        languages=languages,
        statuses=statuses,
        current_status=status,
        current_language=language,
        current_sort=sort,
    )


@app.route("/outreach")
def outreach():
    channels_with_messages = db.get_channels(status="message_ready")
    items = []
    for ch in channels_with_messages:
        messages = db.get_messages(ch["id"])
        if messages:
            items.append({"channel": ch, "message": messages[0]})
    return render_template("outreach.html", items=items)


@app.route("/sent")
def sent_view():
    sent_channels = db.get_channels(status="sent")
    responded_channels = db.get_channels(status="responded")
    all_sent = sent_channels + responded_channels

    items = []
    for ch in all_sent:
        messages = db.get_messages(ch["id"])
        msg = messages[0] if messages else None
        days_since = None
        if msg and msg.get("sent_at"):
            try:
                sent_dt = datetime.fromisoformat(msg["sent_at"])
                days_since = (datetime.now() - sent_dt).days
            except (ValueError, TypeError):
                pass
        items.append({
            "channel": ch,
            "message": msg,
            "days_since_sent": days_since,
            "needs_followup": days_since is not None and days_since >= 5 and not (msg and msg.get("response_received")),
        })

    items.sort(key=lambda x: x.get("days_since_sent") or 0, reverse=True)
    return render_template("sent.html", items=items)


@app.route("/stats")
def stats_view():
    stats = db.get_stats()
    discovery_runs = db.get_discovery_runs()
    return render_template("stats.html", stats=stats, discovery_runs=discovery_runs)


# --- API endpoints ---

@app.route("/api/mark-sent/<int:message_id>", methods=["POST"])
def api_mark_sent(message_id):
    conn = db.get_connection()
    msg = conn.execute("SELECT channel_id FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not msg:
        conn.close()
        return jsonify({"error": "Message not found"}), 404
    channel = db.get_channel_by_id(msg["channel_id"])
    conn.close()
    if channel:
        db.mark_sent(channel["telegram_username"])
    return jsonify({"ok": True})


@app.route("/api/delete-message/<int:message_id>", methods=["POST"])
def api_delete_message(message_id):
    db.delete_message(message_id)
    return jsonify({"ok": True})


@app.route("/api/update-notes/<int:message_id>", methods=["POST"])
def api_update_notes(message_id):
    notes = request.json.get("notes", "")
    db.update_message_notes(message_id, notes)
    return jsonify({"ok": True})


@app.route("/api/record-response/<int:message_id>", methods=["POST"])
def api_record_response(message_id):
    response_text = request.json.get("response_text", "")
    conn = db.get_connection()
    msg = conn.execute("SELECT channel_id FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not msg:
        conn.close()
        return jsonify({"error": "Message not found"}), 404
    channel = db.get_channel_by_id(msg["channel_id"])
    conn.close()
    if channel:
        db.record_response(channel["telegram_username"], response_text)
    return jsonify({"ok": True})


@app.route("/api/mark-no-response/<int:message_id>", methods=["POST"])
def api_mark_no_response(message_id):
    conn = db.get_connection()
    msg = conn.execute("SELECT channel_id FROM messages WHERE id = ?", (message_id,)).fetchone()
    if msg:
        conn.execute(
            "UPDATE channels SET status = 'no_response', updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), msg["channel_id"]),
        )
        conn.commit()
    conn.close()
    return jsonify({"ok": True})


# --- Action endpoints (run discovery, scraping, add channels from UI) ---

@app.route("/api/add-channels", methods=["POST"])
def api_add_channels():
    raw = request.json.get("channels", "")
    usernames = [u.strip() for u in raw.replace(",", " ").split() if u.strip()]
    if not usernames:
        return jsonify({"error": "No channels provided"}), 400
    added = discover.add_channels_manually(usernames)
    return jsonify({"ok": True, "added": added, "count": len(added)})


@app.route("/api/discover", methods=["POST"])
def api_discover():
    source = request.json.get("source", "tgstat")
    category = request.json.get("category", "technology")
    country = request.json.get("country") or None
    pages = request.json.get("pages", 3)
    job_id = f"discover_{source}_{category}_{datetime.now().timestamp()}"

    if source == "tgstat":
        _start_job(job_id, discover.discover_tgstat, category=category, country=country, max_pages=pages)
    elif source == "telemetr":
        _start_job(job_id, discover.discover_telemetr, category=category, max_pages=pages)
    else:
        return jsonify({"error": f"Unknown source: {source}"}), 400

    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    channel = request.json.get("channel")
    limit = request.json.get("limit", 20)
    job_id = f"scrape_{datetime.now().timestamp()}"

    if channel:
        _start_job(job_id, scrape_module.scrape_channels, channel_username=channel)
    else:
        _start_job(job_id, scrape_module.scrape_channels, limit=limit, status="discovered")

    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/scrape-channel/<username>", methods=["POST"])
def api_scrape_single(username):
    job_id = f"scrape_{username}_{datetime.now().timestamp()}"
    _start_job(job_id, scrape_module.scrape_channels, channel_username=username)
    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/job/<job_id>")
def api_job_status(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/cross-references/<username>", methods=["POST"])
def api_cross_references(username):
    found = discover.discover_cross_references(username)
    return jsonify({"ok": True, "found": found, "count": len(found)})


if __name__ == "__main__":
    from config import DASHBOARD_HOST, DASHBOARD_PORT
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=True)

"""Generate static site for GitHub Pages from current DB state."""

import json
import os
import db


def export_data():
    """Export all outreach-relevant data as a JSON blob."""
    channels = db.get_channels()
    all_messages = db.get_messages()
    stats = db.get_stats()
    discovery_runs = db.get_discovery_runs()

    # Build message lookup by channel_id
    msg_by_channel = {}
    for m in all_messages:
        cid = m["channel_id"]
        if cid not in msg_by_channel:
            msg_by_channel[cid] = []
        msg_by_channel[cid].append(m)

    # Enrich channels with their messages
    enriched = []
    for ch in channels:
        ch_copy = dict(ch)
        ch_copy["messages"] = msg_by_channel.get(ch["id"], [])
        # Parse JSON fields
        for field in ("topics", "sample_posts"):
            if ch_copy.get(field) and isinstance(ch_copy[field], str):
                try:
                    ch_copy[field] = json.loads(ch_copy[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        enriched.append(ch_copy)

    return {
        "channels": enriched,
        "stats": stats,
        "discovery_runs": discovery_runs,
    }


def publish(output_dir="docs"):
    """Write the static site to output_dir."""
    data = export_data()
    data_json = json.dumps(data, ensure_ascii=False, default=str, indent=None)

    html = build_html(data_json)

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Static site published to {path}")
    print(f"Channels: {len(data['channels'])}, Messages: {sum(len(c['messages']) for c in data['channels'])}")


def build_html(data_json):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>TG Outreach</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }}
:root {{
  --bg:#111;--card:#1a1a2e;--input:#0f3460;--text:#e6e6e6;--muted:#8a8a9a;
  --accent:#e94560;--accent2:#ff6b81;--success:#2ecc71;--warn:#f39c12;--border:#2a2a4a;--r:10px;
}}
body {{ font-family:-apple-system,system-ui,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; min-height:100dvh; padding-bottom:72px; }}
nav {{ position:sticky;top:0;z-index:100;background:var(--card);border-bottom:1px solid var(--border);display:flex;overflow-x:auto;-webkit-overflow-scrolling:touch;gap:0; }}
nav a {{ flex-shrink:0;padding:14px 16px;color:var(--muted);text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap;border-bottom:2px solid transparent; }}
nav a.active {{ color:var(--accent);border-bottom-color:var(--accent); }}
.page {{ display:none;padding:12px; }}
.page.active {{ display:block; }}
.card {{ background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:14px;margin-bottom:10px; }}
.stats-row {{ display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:12px; }}
.stat {{ background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:12px;text-align:center; }}
.stat .n {{ font-size:1.8rem;font-weight:700;color:var(--accent); }}
.stat .l {{ font-size:0.75rem;color:var(--muted);margin-top:2px; }}
h1 {{ font-size:1.3rem;margin-bottom:10px; }}
h2 {{ font-size:1.1rem;margin-bottom:8px; }}

/* Outreach card */
.outreach-card {{ margin-bottom:14px; }}
.outreach-header {{ display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:8px; }}
.channel-name {{ font-weight:700;font-size:1rem; }}
.channel-meta {{ font-size:0.8rem;color:var(--muted);margin-top:2px; }}
.admin-link {{
  display:inline-flex;align-items:center;gap:6px;
  background:var(--accent);color:#fff;padding:8px 14px;border-radius:var(--r);
  text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;
  min-height:44px;
}}
.admin-link:active {{ background:var(--accent2); }}
.admin-link svg {{ width:18px;height:18px;fill:currentColor;flex-shrink:0; }}
.msg-box {{
  background:var(--input);border:1px solid var(--border);border-radius:var(--r);
  padding:12px;white-space:pre-wrap;font-size:0.9rem;line-height:1.5;
  position:relative;user-select:text;-webkit-user-select:text;
  word-break:break-word;
}}
.copy-btn {{
  display:block;width:100%;margin-top:8px;padding:12px;
  background:var(--success);color:#fff;border:none;border-radius:var(--r);
  font-size:0.95rem;font-weight:600;cursor:pointer;min-height:48px;
}}
.copy-btn:active {{ background:#27ae60; }}
.copy-btn.copied {{ background:var(--accent); }}

/* Channel list */
.ch-row {{ padding:10px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;gap:8px; }}
.ch-row:last-child {{ border-bottom:none; }}
.ch-info {{ flex:1;min-width:0; }}
.ch-title {{ font-weight:600;font-size:0.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }}
.ch-detail {{ font-size:0.78rem;color:var(--muted); }}
.badge {{
  display:inline-block;padding:3px 8px;border-radius:10px;font-size:0.7rem;font-weight:600;white-space:nowrap;flex-shrink:0;
}}
.badge-discovered {{ background:#222;color:var(--muted); }}
.badge-scraped {{ background:#1a3a5c;color:#5dade2; }}
.badge-message_ready {{ background:#1a3c1a;color:var(--success); }}
.badge-sent {{ background:#3c3a1a;color:var(--warn); }}
.badge-responded {{ background:#1a3c2a;color:#2ecc71; }}
.badge-no_response {{ background:#2a2a2a;color:#888; }}

/* Sent tracking */
.followup {{ border-left:3px solid var(--warn);padding-left:10px; }}
.days-badge {{ font-size:0.75rem;padding:2px 6px;border-radius:8px;font-weight:600; }}
.days-overdue {{ background:rgba(243,156,18,0.2);color:var(--warn); }}
.days-ok {{ background:rgba(46,204,113,0.1);color:var(--success); }}
.response-box {{ background:rgba(46,204,113,0.1);border:1px solid var(--success);border-radius:var(--r);padding:10px;margin-top:8px;font-size:0.85rem; }}

/* Funnel */
.funnel {{ display:flex;align-items:center;gap:4px;overflow-x:auto;margin-bottom:12px;padding-bottom:4px; }}
.funnel-step {{ text-align:center;padding:8px 10px;border-radius:var(--r);background:var(--card);border:1px solid var(--border);flex-shrink:0;min-width:70px; }}
.funnel-step .fc {{ font-size:1.3rem;font-weight:700;color:var(--accent); }}
.funnel-step .fl {{ font-size:0.65rem;color:var(--muted);text-transform:uppercase; }}
.funnel-arr {{ color:var(--muted);font-size:1rem; }}

/* Filters */
.filters {{ display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap; }}
.filters select {{ background:var(--input);border:1px solid var(--border);color:var(--text);padding:8px;border-radius:var(--r);font-size:0.85rem;min-height:40px; }}

/* Details expand */
details {{ margin-top:8px; }}
details summary {{ color:var(--accent);font-size:0.82rem;cursor:pointer;padding:4px 0; }}
details .post-snippet {{ background:var(--bg);border-radius:var(--r);padding:8px;margin:4px 0;font-size:0.8rem;line-height:1.4; }}

/* Empty state */
.empty {{ text-align:center;padding:40px 20px;color:var(--muted); }}

@media(min-width:600px) {{
  body {{ max-width:800px;margin:0 auto; }}
  .stats-row {{ grid-template-columns:repeat(4,1fr); }}
}}
</style>
</head>
<body>

<nav id="nav">
  <a href="#" data-tab="outreach" class="active">Outreach</a>
  <a href="#" data-tab="sent">Sent</a>
  <a href="#" data-tab="channels">Channels</a>
  <a href="#" data-tab="pipeline">Pipeline</a>
</nav>

<div id="outreach" class="page active"></div>
<div id="sent" class="page"></div>
<div id="channels" class="page"></div>
<div id="pipeline" class="page"></div>

<script>
const DATA = {data_json};
const TG_ICON = '<svg viewBox="0 0 24 24"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>';

// --- Tab switching ---
document.querySelectorAll('#nav a').forEach(a => {{
  a.addEventListener('click', e => {{
    e.preventDefault();
    document.querySelectorAll('#nav a').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
    a.classList.add('active');
    document.getElementById(a.dataset.tab).classList.add('active');
  }});
}});

// --- Copy ---
function copyMsg(id) {{
  const el = document.getElementById('msg-'+id);
  const btn = document.getElementById('btn-'+id);
  const text = el.innerText;
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy Message'; btn.classList.remove('copied'); }}, 2000);
  }}).catch(() => {{
    // Fallback for older mobile browsers
    const range = document.createRange();
    range.selectNodeContents(el);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    document.execCommand('copy');
    sel.removeAllRanges();
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy Message'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

// --- Helpers ---
function fmt(n) {{ return n ? n.toLocaleString() : '-'; }}
function badge(status) {{ return `<span class="badge badge-${{status}}">${{status}}</span>`; }}
function tgLink(username) {{
  if (!username) return '';
  username = username.replace(/^@/, '');
  return `<a href="https://t.me/${{username}}" target="_blank" rel="noopener" class="admin-link">${{TG_ICON}}DM @${{username}}</a>`;
}}
function daysSince(dateStr) {{
  if (!dateStr) return null;
  const d = new Date(dateStr);
  const now = new Date();
  return Math.floor((now - d) / 86400000);
}}

// --- Render Outreach ---
function renderOutreach() {{
  const el = document.getElementById('outreach');
  const items = DATA.channels.filter(c => c.status === 'message_ready' && c.messages.length > 0);

  if (!items.length) {{
    el.innerHTML = '<div class="empty"><h2>No messages in queue</h2><p>Generate messages first</p></div>';
    return;
  }}

  el.innerHTML = `<h1>Outreach Queue (${{items.length}})</h1>` + items.map(ch => {{
    const msg = ch.messages[0];
    return `
      <div class="card outreach-card">
        <div class="outreach-header">
          <div>
            <div class="channel-name">@${{ch.telegram_username}}</div>
            <div class="channel-meta">${{ch.title || ''}} &middot; ${{fmt(ch.subscriber_count)}} subs &middot; ${{ch.language || '?'}}</div>
          </div>
          ${{tgLink(ch.admin_username)}}
        </div>
        <div class="msg-box" id="msg-${{msg.id}}">${{msg.message_text}}</div>
        <button class="copy-btn" id="btn-${{msg.id}}" onclick="copyMsg(${{msg.id}})">Copy Message</button>
      </div>`;
  }}).join('');
}}

// --- Render Sent ---
function renderSent() {{
  const el = document.getElementById('sent');
  const items = DATA.channels.filter(c => c.status === 'sent' || c.status === 'responded' || c.status === 'no_response');

  if (!items.length) {{
    el.innerHTML = '<div class="empty"><h2>No messages sent yet</h2></div>';
    return;
  }}

  el.innerHTML = `<h1>Sent (${{items.length}})</h1>` + items.map(ch => {{
    const msg = ch.messages[0];
    const days = msg ? daysSince(msg.sent_at) : null;
    const overdue = days !== null && days >= 5 && ch.status === 'sent';
    return `
      <div class="card ${{overdue ? 'followup' : ''}}">
        <div class="outreach-header">
          <div>
            <div class="channel-name">@${{ch.telegram_username}} ${{days !== null ? `<span class="days-badge ${{overdue ? 'days-overdue' : 'days-ok'}}">${{days}}d ago</span>` : ''}}</div>
            <div class="channel-meta">${{ch.title || ''}} &middot; ${{fmt(ch.subscriber_count)}} subs &middot; ${{badge(ch.status)}}</div>
          </div>
          ${{tgLink(ch.admin_username)}}
        </div>
        ${{msg ? `<details><summary>Sent message</summary><div class="msg-box" style="margin-top:6px">${{msg.message_text}}</div></details>` : ''}}
        ${{msg && msg.response_received && msg.response_text ? `<div class="response-box"><strong>Response:</strong> ${{msg.response_text}}</div>` : ''}}
      </div>`;
  }}).join('');
}}

// --- Render Channels ---
function renderChannels(filter) {{
  const el = document.getElementById('channels');
  let items = DATA.channels;

  // Get unique languages and statuses
  const languages = [...new Set(items.map(c => c.language).filter(Boolean))].sort();
  const statuses = [...new Set(items.map(c => c.status).filter(Boolean))].sort();

  let filterHTML = `<div class="filters">
    <select id="f-status" onchange="renderChannels(true)">
      <option value="">All</option>
      ${{statuses.map(s => `<option value="${{s}}">${{s}}</option>`).join('')}}
    </select>
    <select id="f-lang" onchange="renderChannels(true)">
      <option value="">All langs</option>
      ${{languages.map(l => `<option value="${{l}}">${{l}}</option>`).join('')}}
    </select>
  </div>`;

  if (filter) {{
    const fs = document.getElementById('f-status')?.value || '';
    const fl = document.getElementById('f-lang')?.value || '';
    if (fs) items = items.filter(c => c.status === fs);
    if (fl) items = items.filter(c => c.language === fl);
    // Keep filter values
    filterHTML = filterHTML.replace(`value="${{fs}}"`, `value="${{fs}}" selected`).replace(`value="${{fl}}"`, `value="${{fl}}" selected`);
  }}

  items.sort((a,b) => (b.subscriber_count||0) - (a.subscriber_count||0));

  el.innerHTML = `<h1>Channels (${{items.length}})</h1>${{filterHTML}}<div class="card">` + items.map(ch => `
    <div class="ch-row">
      <div class="ch-info">
        <div class="ch-title">@${{ch.telegram_username}}</div>
        <div class="ch-detail">${{ch.title || ''}} &middot; ${{fmt(ch.subscriber_count)}} &middot; ${{ch.language || '?'}} ${{ch.admin_username ? '&middot; @'+ch.admin_username : ''}}</div>
      </div>
      ${{badge(ch.status)}}
    </div>`).join('') + '</div>';
}}

// --- Render Pipeline ---
function renderPipeline() {{
  const el = document.getElementById('pipeline');
  const s = DATA.stats;
  const bs = s.by_status || {{}};

  el.innerHTML = `
    <h1>Pipeline</h1>
    <div class="funnel">
      <div class="funnel-step"><div class="fc">${{bs.discovered||0}}</div><div class="fl">Discovered</div></div>
      <span class="funnel-arr">&rarr;</span>
      <div class="funnel-step"><div class="fc">${{bs.scraped||0}}</div><div class="fl">Scraped</div></div>
      <span class="funnel-arr">&rarr;</span>
      <div class="funnel-step"><div class="fc">${{bs.message_ready||0}}</div><div class="fl">Ready</div></div>
      <span class="funnel-arr">&rarr;</span>
      <div class="funnel-step"><div class="fc">${{bs.sent||0}}</div><div class="fl">Sent</div></div>
      <span class="funnel-arr">&rarr;</span>
      <div class="funnel-step"><div class="fc">${{bs.responded||0}}</div><div class="fl">Replied</div></div>
    </div>
    <div class="stats-row">
      <div class="stat"><div class="n">${{s.total_channels}}</div><div class="l">Channels</div></div>
      <div class="stat"><div class="n">${{s.total_messages}}</div><div class="l">Messages</div></div>
      <div class="stat"><div class="n">${{s.messages_sent}}</div><div class="l">Sent</div></div>
      <div class="stat"><div class="n">${{s.response_rate}}%</div><div class="l">Response Rate</div></div>
    </div>
    ${{Object.keys(s.by_language || {{}}).length ? `
    <div class="card">
      <h2>By Language</h2>
      ${{Object.entries(s.by_language).map(([l,c]) => `
        <div class="ch-row">
          <div class="ch-info"><div class="ch-title">${{l||'Unknown'}}</div></div>
          <span style="color:var(--accent);font-weight:700">${{c}}</span>
        </div>`).join('')}}
    </div>` : ''}}
  `;
}}

// --- Init ---
renderOutreach();
renderSent();
renderChannels();
renderPipeline();
</script>
</body>
</html>'''


if __name__ == "__main__":
    publish()

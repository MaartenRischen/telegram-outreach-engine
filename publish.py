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

    # Generate English translations for non-English messages
    translations = {
        'ai_machinelearning_big_data': "Hey! Subscribed to the channel, great presentation of LLM stuff.\n\nI'm Maarten, a developer from Holland. Built something that fixes the main problem with neural networks - hallucinations.\n\nTriall works like this: three models from different companies answer the same question independently. Then they anonymously peer-review each other, attack arguments, verify facts. Like peer review in science. Made-up stuff simply doesn't pass.\n\nExample: Gemini generated entire scientific papers with non-existent authors, journals and DOIs. Looked convincing. Two other models tore it apart during review.\n\nA regular neural network agrees with you. Here three models argue with each other and find the truth.\n\nWant to give you a free subscription forever, just to try it out.",
        'gpt_news': "Hey! I read the channel, love the way you present news.\n\nI'm Maarten from Holland. Built Triall - essentially a cure for neural network hallucinations.\n\nHow it works: three models from different providers answer a question in parallel. Then they blindly review each other, find errors, attack weak arguments. Made-up facts don't pass because other models catch them.\n\nReal case: Gemini made up scientific papers with fake authors and DOIs. One model would have missed it. Three models in peer review mode found it in seconds.\n\nNeural networks are trained to agree with the user. Triall makes them argue with each other. A fundamentally different interaction pattern.\n\nWant to give you a free subscription forever, just to try it out.",
        'ai_newz': "Hey! You can tell there's real research experience behind the channel. Quality breakdowns.\n\nI'm Maarten, a developer from Holland. Built Triall - a platform that solves hallucinations through adversarial reasoning.\n\nThree models from different companies answer independently, then conduct anonymous peer review. Attack each other's arguments, verify facts, find logical holes. Based on the H-Neurons paper (Tsinghua, arXiv 2512.01797).\n\nIn practice this kills hallucinations: Gemini fabricated entire scientific papers with fake authors and DOIs. Two other models found it and tore it apart.\n\nOne model agrees with you. Three models blindly search for truth.\n\nWant to give you a free subscription forever, just to try it out.",
        'opendatascience': "Hey! Been following ODS for a while, strong community.\n\nI'm Maarten from Holland. Built Triall - a tool that fixes neural network hallucinations through adversarial reasoning.\n\nThree models from different providers answer a question independently, then anonymously review each other. Find errors, attack arguments, verify facts. Like peer review in science, but for LLMs.\n\nExample: Gemini made up scientific papers with non-existent authors and DOIs. One model would have accepted it as truth. Three models in review mode exposed it.\n\nBased on H-Neurons paper (Tsinghua, arXiv 2512.01797).\n\nWant to give you a free subscription forever, just to try it out.",
        'gonzo_ml': "Hey! Your ML paper reviews are some of the best in Russian.\n\nI'm Maarten from Holland, building Triall. Essentially a cure for hallucinations: three models from different companies answer in parallel, then conduct blind peer review and attack each other's arguments.\n\nMade-up facts simply don't survive. In testing, Gemini generated scientific papers with fake authors and DOIs. The other models caught it during review.\n\nA regular LLM agrees with you (sycophancy). Three models blindly search for truth. Fundamentally different pattern.\n\nBased on H-Neurons paper (Tsinghua, arXiv 2512.01797).\n\nWant to give you a free subscription forever, just to try it out.",
        'machinelearning_ru': "Hey! Saw the post about CodePilot for Claude Code, good content.\n\nI'm Maarten, a developer from Holland. Built Triall - a fix for neural network hallucinations.\n\nThree models from different providers answer a question in parallel, then anonymously review each other. Attack arguments, verify facts, find logical holes. Made-up stuff doesn't pass.\n\nReal example: Gemini fabricated scientific papers with non-existent authors and DOIs. Looked plausible. Two other models exposed it in peer review.\n\nLLMs are trained to agree with you. Triall makes them argue with each other and find the truth.\n\nWant to give you a free subscription forever, just to try it out.",
        'neuraldeep': "Hey! Impressive journey from IT Admin to Head of AI in 5 years, and gptdaisy with 100k MAU is a serious project.\n\nI'm Maarten from Holland. Built Triall - essentially a hallucination killer.\n\nThree models from different companies answer independently, then conduct anonymous peer review: attack each other's arguments, verify facts. Made-up stuff doesn't pass.\n\nGemini in testing fabricated scientific papers with fake authors and DOIs. One model would have missed it. Three models in review mode tore it apart in seconds.\n\nA neural network agrees with you. Three neural networks argue and find the truth.\n\nWant to give you a free subscription forever, just to try it out.",
        'oestick': "Hey! Channel is fire. The post about bypassing Codex limitations - spot on, and the coding agent on phone via Termius is practical.\n\nI'm Maarten from Holland. You write about pitfalls with AI. Here's the biggest pitfall everyone steps on: hallucinations.\n\nBuilt Triall. Three models from different providers answer independently, then blindly review each other. Attack arguments, verify facts. Made-up stuff doesn't pass.\n\nGemini in testing made up entire scientific papers with non-existent authors. One model would have swallowed it. Three models in peer review mode caught it.\n\nModels are trained to agree with you. Triall makes them argue with each other.\n\nWant to give you a free subscription forever, just to try it out.",
        'nobilix': "Hey! Love the no-hype approach, and the post about Opus 4.6 vs GPT-5.3-Codex was great.\n\nI'm Maarten from Holland. Built Triall - a fix for the main problem with neural networks: hallucinations.\n\nThree models from different companies answer in parallel, then anonymously review each other. Find errors, attack arguments, verify facts. Made-up stuff doesn't survive.\n\nGemini fabricated scientific papers with fake authors and DOIs. Sounded convincing. The other two models found it during review.\n\nA regular LLM agrees with you. Three models argue and find the truth.\n\nBased on H-Neurons paper (Tsinghua, arXiv 2512.01797).\n\nWant to give you a free subscription forever, just to try it out.",
        'the_ai_architect': "Hey! The post about 'from 40 developers down to 10' and restructuring for AI - really important topic.\n\nI'm Maarten from Holland. Built Triall - a tool that kills neural network hallucinations.\n\nThree models from different providers work in parallel: answer independently, then anonymously review each other. Attack arguments, catch made-up facts, find logical holes.\n\nWhen you work with one model, it agrees with you. When three models check each other blindly, hallucinations don't pass. Gemini in testing made up scientific papers with fake authors and DOIs. Other models caught it.\n\nWant to give you a free subscription forever, just to try it out.",
        'countwithsasha': "Hey! Posts about Mac Mini for bots and OpenClaw for 100 rub/week - practical content, love it.\n\nI'm Maarten from Holland. You write about AI use cases. Here's a use case: the main problem with neural networks - hallucinations.\n\nBuilt Triall. Three models from different companies answer in parallel, then blindly review each other. Attack arguments, verify facts. Made-up stuff doesn't pass.\n\nGemini in testing generated scientific papers with fake authors and DOIs. One model would have accepted it as truth. Three models in review exposed it.\n\nA model agrees with you. Three models argue and find the truth.\n\nWant to give you a free subscription forever, just to try it out.",
        'deeplearning_ru': "Hey! The post about 16 Claude agents building a C compiler for $20k - impressive.\n\nI'm Maarten from Holland. Built Triall - a fix for neural network hallucinations.\n\nThree models from different providers answer independently, then anonymously review each other. Attack arguments, verify facts, find logical holes. Made-up stuff doesn't pass.\n\nGemini fabricated scientific papers with non-existent authors and DOIs. Other models found it during review. One model would have missed it.\n\nA regular neural network agrees with you. Three neural networks argue and find the truth.\n\nWant to give you a free subscription forever, just to try it out.",
        'evilfreelancer': "Hey Pavel!\n\nI'm Maarten from Holland. Built Triall - a fix for the hallucination problem.\n\nThree models from different companies answer in parallel, then anonymously review each other. Made-up facts don't pass peer review.\n\nGemini made up scientific papers with fake DOIs. Three models caught it. One would have missed it.\n\nA model agrees with you. Three models argue and find the truth.\n\nWant to give you a free subscription forever, just to try it out.",
    }

    return {
        "channels": enriched,
        "stats": stats,
        "discovery_runs": discovery_runs,
        "translations": translations,
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
.outreach-header {{ margin-bottom:10px; }}
.channel-name {{ font-weight:700;font-size:1rem; }}
.channel-name a {{ color:var(--text);text-decoration:none; }}
.channel-meta {{ font-size:0.8rem;color:var(--muted);margin-top:2px; }}
.action-row {{ display:flex;gap:8px;margin-top:10px; }}
.action-row a {{ flex:1;text-align:center; }}
.channel-link {{
  display:inline-flex;align-items:center;justify-content:center;gap:6px;
  background:var(--input);border:1px solid var(--border);color:var(--text);padding:10px 14px;border-radius:var(--r);
  text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;
  min-height:44px;
}}
.channel-link:active {{ background:var(--border); }}
.admin-link {{
  display:inline-flex;align-items:center;justify-content:center;gap:6px;
  background:var(--accent);color:#fff;padding:10px 14px;border-radius:var(--r);
  text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;
  min-height:44px;
}}
.admin-link:active {{ background:var(--accent2); }}
.admin-link svg, .channel-link svg {{ width:18px;height:18px;fill:currentColor;flex-shrink:0; }}
.no-admin {{ display:inline-flex;align-items:center;justify-content:center;gap:6px;background:var(--border);color:var(--muted);padding:10px 14px;border-radius:var(--r);font-size:0.85rem;font-weight:600;min-height:44px;flex:1;text-align:center; }}
.msg-box {{
  background:var(--input);border:1px solid var(--border);border-radius:var(--r);
  padding:12px;white-space:pre-wrap;font-size:0.9rem;line-height:1.5;
  position:relative;user-select:text;-webkit-user-select:text;
  word-break:break-word;
}}
.btn-row {{ display:flex;gap:8px;margin-top:8px; }}
.copy-btn {{
  flex:1;padding:12px;
  background:var(--success);color:#fff;border:none;border-radius:var(--r);
  font-size:0.95rem;font-weight:600;cursor:pointer;min-height:48px;
}}
.copy-btn:active {{ background:#27ae60; }}
.copy-btn.copied {{ background:var(--accent); }}
.sent-btn {{
  padding:12px 16px;
  background:var(--warn);color:#fff;border:none;border-radius:var(--r);
  font-size:0.95rem;font-weight:600;cursor:pointer;min-height:48px;white-space:nowrap;
}}
.sent-btn:active {{ background:#e67e22; }}
.undo-btn {{
  padding:8px 14px;
  background:var(--border);color:var(--text);border:none;border-radius:var(--r);
  font-size:0.82rem;cursor:pointer;min-height:40px;
}}
.translation {{
  background:rgba(46,204,113,0.08);border:1px solid rgba(46,204,113,0.2);border-radius:var(--r);
  padding:10px;margin-top:8px;font-size:0.85rem;line-height:1.5;white-space:pre-wrap;display:none;
}}
.translation.show {{ display:block; }}
.translate-toggle {{
  background:none;border:1px solid var(--border);color:var(--muted);padding:6px 10px;
  border-radius:var(--r);font-size:0.78rem;cursor:pointer;margin-top:6px;
}}

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

// --- Sent tracking (localStorage) ---
function getSentData() {{
  try {{ return JSON.parse(localStorage.getItem('tg_sent') || '{{}}'); }} catch {{ return {{}}; }}
}}
function markAsSent(username) {{
  const d = getSentData();
  d[username] = {{ sent_at: new Date().toISOString() }};
  localStorage.setItem('tg_sent', JSON.stringify(d));
  renderOutreach();
  renderSent();
  // Update sent tab count
  const sentCount = Object.keys(getSentData()).length;
  document.querySelector('[data-tab="sent"]').textContent = `Sent (${{sentCount}})`;
}}
function undoSent(username) {{
  const d = getSentData();
  delete d[username];
  localStorage.setItem('tg_sent', JSON.stringify(d));
  renderOutreach();
  renderSent();
  const sentCount = Object.keys(getSentData()).length;
  document.querySelector('[data-tab="sent"]').textContent = `Sent (${{sentCount}})`;
}}
function isSent(username) {{
  return !!getSentData()[username];
}}

// --- Helpers ---
function fmt(n) {{ return n ? n.toLocaleString() : '-'; }}
function badge(status) {{ return `<span class="badge badge-${{status}}">${{status}}</span>`; }}
function tgDmLink(username) {{
  if (!username) return '<span class="no-admin">No admin found</span>';
  username = username.replace(/^@/, '');
  return `<a href="https://t.me/${{username}}" target="_blank" rel="noopener" class="admin-link">${{TG_ICON}}DM @${{username}}</a>`;
}}
function tgChannelLink(username) {{
  username = username.replace(/^@/, '');
  return `<a href="https://t.me/s/${{username}}" target="_blank" rel="noopener" class="channel-link">${{TG_ICON}}View Channel</a>`;
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

  const unsent = items.filter(ch => !isSent(ch.telegram_username));
  const translations = DATA.translations || {{}};
  el.innerHTML = `<h1>Outreach Queue (${{unsent.length}})</h1>` + (unsent.length ? unsent.map(ch => {{
    const msg = ch.messages[0];
    const tr = translations[ch.telegram_username];
    return `
      <div class="card outreach-card">
        <div class="outreach-header">
          <div class="channel-name">${{ch.title || '@'+ch.telegram_username}}</div>
          <div class="channel-meta">${{fmt(ch.subscriber_count)}} subs &middot; ${{ch.language || '?'}} &middot; @${{ch.telegram_username}}</div>
        </div>
        <div class="msg-box" id="msg-${{msg.id}}">${{msg.message_text}}</div>
        ${{tr ? `<button class="translate-toggle" onclick="this.nextElementSibling.classList.toggle('show');this.textContent=this.textContent==='EN'?'Hide EN':'EN'">EN</button><div class="translation">${{tr}}</div>` : ''}}
        <div class="btn-row">
          <button class="copy-btn" id="btn-${{msg.id}}" onclick="copyMsg(${{msg.id}})">Copy Message</button>
          <button class="sent-btn" onclick="markAsSent('${{ch.telegram_username}}')">Sent</button>
        </div>
        <div class="action-row">
          ${{tgChannelLink(ch.telegram_username)}}
          ${{tgDmLink(ch.admin_username)}}
        </div>
      </div>`;
  }}).join('') : '<div class="empty"><h2>All done!</h2><p>All messages have been sent</p></div>');
}}

// --- Render Sent ---
function renderSent() {{
  const el = document.getElementById('sent');
  const sentData = getSentData();

  // Combine: DB-tracked sent + localStorage-tracked sent
  const dbSent = DATA.channels.filter(c => c.status === 'sent' || c.status === 'responded' || c.status === 'no_response');
  const localSent = DATA.channels.filter(c => c.status === 'message_ready' && sentData[c.telegram_username] && c.messages.length > 0);
  const allSent = [...localSent, ...dbSent];

  if (!allSent.length) {{
    el.innerHTML = '<div class="empty"><h2>No messages sent yet</h2></div>';
    return;
  }}

  el.innerHTML = `<h1>Sent (${{allSent.length}})</h1>` + allSent.map(ch => {{
    const msg = ch.messages[0];
    const localEntry = sentData[ch.telegram_username];
    const sentAt = (msg && msg.sent_at) || (localEntry && localEntry.sent_at);
    const days = daysSince(sentAt);
    const overdue = days !== null && days >= 5 && ch.status !== 'responded';
    return `
      <div class="card ${{overdue ? 'followup' : ''}}">
        <div class="outreach-header">
          <div class="channel-name">${{ch.title || '@'+ch.telegram_username}} ${{days !== null ? `<span class="days-badge ${{overdue ? 'days-overdue' : 'days-ok'}}">${{days}}d</span>` : ''}}</div>
          <div class="channel-meta">${{fmt(ch.subscriber_count)}} subs &middot; @${{ch.telegram_username}} &middot; ${{ch.status === 'responded' ? badge('responded') : badge('sent')}}</div>
        </div>
        <div class="action-row" style="margin-bottom:8px">
          ${{tgChannelLink(ch.telegram_username)}}
          ${{tgDmLink(ch.admin_username)}}
        </div>
        ${{msg ? `<details><summary>Sent message</summary><div class="msg-box" style="margin-top:6px">${{msg.message_text}}</div></details>` : ''}}
        ${{msg && msg.response_received && msg.response_text ? `<div class="response-box"><strong>Response:</strong> ${{msg.response_text}}</div>` : ''}}
        ${{localEntry ? `<button class="undo-btn" style="margin-top:8px" onclick="undoSent('${{ch.telegram_username}}')">Undo</button>` : ''}}
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
// Update sent tab count on load
const sentCount = Object.keys(getSentData()).length;
if (sentCount) document.querySelector('[data-tab="sent"]').textContent = `Sent (${{sentCount}})`;
</script>
</body>
</html>'''


if __name__ == "__main__":
    publish()

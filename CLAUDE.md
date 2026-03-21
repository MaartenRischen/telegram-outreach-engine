# Telegram Outreach Engine for Triall

## What This Project Does
Discovers AI/tech Telegram channels, scrapes their public data, and prepares outreach messages for Triall.ai. Claude Code generates the messages; Maarten sends them manually.

## Message Generation Workflow
1. Run `python cli.py ready` to see scraped channels awaiting messages
2. Run `python cli.py show @channelname` for full channel details
3. Read the channel data and generate a personalized outreach message
4. Run `python cli.py message @channelname "the generated message"` to store it

## Product Context: Triall.ai
- Multi-AI adversarial reasoning platform
- Three models answer independently, peer-review anonymously, synthesize, verify claims
- Based on H-Neurons paper (Tsinghua, arXiv 2512.01797)
- Proof points: Gemini fabricating entire papers with fake authors/journals/DOIs caught by peer review; Gemini inventing file paths caught by peer review
- Tiers: Free trial, Reasoner $15, Architect $39, Collective $99

## The Offer
- Free Architect account ($39/mo) for unlimited time
- No obligations, no conditions

## Outreach Rules (non-negotiable)
- NO em-dashes. Ever.
- Don't educate the admin on their own topic
- Don't assume they missed major research
- Frame as "I built this thing" not "here's something you don't know"
- Match the channel's energy and tone
- Keep it under 200 words
- Include the relevant language-specific landing page URL with UTM: `https://triall.ai?lng={lang}&utm_source=telegram&utm_medium=outreach&utm_campaign={channel_username}`
- Don't mention specific ad spend or revenue numbers
- Sound like a real person, not a marketing message
- If the channel recently posted about AI accuracy, hallucination, or multi-model approaches, reference that specific post
- Maarten is Dutch, based in Thailand, solo founder, musician background, direct and warm

## What Worked (the Нейроскуф post pattern)
- Led with the sycophancy problem (LLMs trained to agree with you)
- Positioned Triall as "a completely different interaction pattern"
- Explained three models working in parallel simply
- Described adversarial process (different angles, challenging arguments, finding logical holes)
- Ended with genuine enthusiasm
- Was NOT a pitch, was a tool recommendation

## Landing Page URLs
- Russian: https://triall.ai?lng=ru
- English: https://triall.ai?lng=en
- German: https://triall.ai?lng=de
- French: https://triall.ai?lng=fr
- Spanish: https://triall.ai?lng=es
- Portuguese: https://triall.ai?lng=pt
- Japanese: https://triall.ai?lng=ja
- Korean: https://triall.ai?lng=ko
- Chinese: https://triall.ai?lng=zh
- Turkish: https://triall.ai?lng=tr
- Arabic: https://triall.ai?lng=ar
- Hindi: https://triall.ai?lng=hi
- Dutch: https://triall.ai?lng=nl
- Thai: https://triall.ai?lng=th
- Italian: https://triall.ai?lng=it
- Polish: https://triall.ai?lng=pl
- Vietnamese: https://triall.ai?lng=vi
- Indonesian: https://triall.ai?lng=id

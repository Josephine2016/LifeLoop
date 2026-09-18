LifeLoop — Your Everyday Life Admin Agent

AWS Strands Agents Hackathon — Everyday Agents Track

LifeLoop is an autonomous agent that manages the boring life admin you forget until it's late: PHCN bills, groceries, subscriptions, and receipts.

Built with Strands Agents SDK on AWS Bedrock (Claude Haiku 4.5 in us-west-2).



🎯 Problem

In Lagos (and everywhere), people juggle:

PHCN / utility bills with no reminders → disconnection

Groceries forgotten until market day is over

Subscriptions (Netflix, Spotify, data) auto-renewing and draining money

Receipts piled up with no tracking

Existing tools are dashboards. You still have to DO the work.

💡 Solution: Autonomous Tools, Not a Dashboard

LifeLoop is a functional agent — you tell it in natural language, it decides which tool to call.

"I have PHCN 15000 due Sept 20 and Netflix 2000 monthly, and I need rice 5kg"

Agent automatically:

Calls add\_bill(PHCN, 15000, 2026-09-20, monthly, utilities)

Calls add\_bill(Netflix, 2000, 2026-09-15, monthly, entertainment)

Calls manage\_groceries(rice 5kg, add)

Calls check\_due\_bills(7) to warn you

Calls search\_best\_practices("how to save on PHCN bill Lagos") — demonstrates correct specific search query (not generic 'bills')

No buttons. No forms. Just talk.

🛠️ 6 Tools Built (All @tool Decorated)

add\_bill — name, amount, due\_date, recurrence, category, reminder 3 days before

check\_due\_bills — shows upcoming bills within N days

scan\_receipt — parses text receipt → extracts amount/items (local, no cloud OCR needed for MVP)

manage\_groceries — add/list/clear grocery list persisted in JSON

audit\_subscriptions — finds duplicate subscriptions + total monthly spend

search\_best\_practices — Tavily/Exa ready, returns specific queries like 'how to save on PHCN bill Lagos' (hackathon-compliant)

All tools persist to /data/ — ready for Bedrock AgentCore deployment.

🏗️ Architecture

User Message (Natural Language)

&#x20;  ↓

Strands Agent (System Prompt + Tools)

&#x20;  ↓

AWS Bedrock Model: anthropic.claude-haiku-4-5 in us-west-2

&#x20;  ↓

Tool Router (Autonomous Decision)

&#x20;  ├── add\_bill → data/bills.json

&#x20;  ├── check\_due\_bills → reads bills.json

&#x20;  ├── scan\_receipt → parses \& adds to bills/groceries

&#x20;  ├── manage\_groceries → data/grocery.json

&#x20;  ├── audit\_subscriptions → data/bills.json analysis

&#x20;  └── search\_best\_practices → web search (Tavily/Exa) with SPECIFIC query

&#x20;  ↓

Response (Summary of actions taken)

Meets Objectives:

✅ Everyday Agents Track: bill management, groceries, life admin

✅ Functional tools, not just dashboard

✅ Search done RIGHT: specific queries

✅ Ready for AgentCore (tools are stateless, JSON persisted)

🚀 Local Test (What Judges Saw)

bash

pip install strands-agents strands-agents-tools boto3 python-dotenv

export AWS\_REGION=us-west-2

python agent.py

Output from screenshot:

Bill added: PHCN - 15000 due 2026-09-20 (monthly). I'll remind you 3 days before.

Bill added: Netflix - 2000 due 2026-09-15 (monthly).

Added to grocery list: rice (5kg)

Upcoming bills: PHCN: 15000 due 2026-09-20, Netflix: 2000 due 2026-09-15

Subscription Audit: 1 subs, total monthly 2000. No duplicates found.

\[SEARCH READY] Would search web for: 'how to save on PHCN bill Lagos'

All tools work - ready for Bedrock AgentCore!

📦 Files

agent.py — Main agent with 6 @tool functions + BedrockModel

data/ — bills.json, grocery.json (auto-created)

.env — AWS\_REGION=us-west-2

requirements.txt

README.md (this)

🎥 Demo Video Script (2 min)

0:00-0:15 Problem: Show PHCN bill paper, phone with no reminders

0:15-0:45 Show code: 6 @tool functions in agent.py

0:45-1:15 Live terminal: python agent.py → adds PHCN, Netflix, rice, checks due, audit

1:15-1:45 Show Bedrock console: Claude Haiku 4.5 in us-west-2 Workbench = subscribed

1:45-2:00 Future: Deploy to AgentCore, WhatsApp integration for Lagos market women, voice reminders in Pidgin

🌍 Why Lagos?

Built for Lagos reality: PHCN, not PG\&E. Naira, not dollars. Market list, not Whole Foods. Solves real pain for 36-year-old working professionals juggling family + work.

🔮 Next

Deploy to Bedrock AgentCore

Add WhatsApp via Twilio (tell LifeLoop via WhatsApp)

Voice reminders

Receipt image OCR with Textract

Built by Josephine Chukwu-Onwuchuruba — Lagos, Nigeria

















&#x20;




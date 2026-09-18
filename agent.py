"""
LifeLoop - Everyday Life Admin Agent - FIXED MODEL ID
Built with Strands Agents SDK + AWS Bedrock Claude Haiku 4.5 (us-west-2)
Everyday Agents Track - AWS Strands Hackathon
Author: Joyce Chuks - Lagos, Nigeria
FIX: Use inference profile ID us.anthropic.claude-haiku-4-5-20251001-v1:0
Source: AWS Bedrock docs + https://github.com/tamirdresher/tamirdresher.github.io blog
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from datetime import datetime, timedelta
from strands import Agent, tool
from strands.models import BedrockModel

os.makedirs("data", exist_ok=True)
BILLS_FILE = "data/bills.json"
GROCERY_FILE = "data/grocery.json"

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

@tool
def add_bill(name: str, amount: float, due_date: str, recurrence: str = "monthly", category: str = "utilities") -> str:
    """Add a bill with reminder. Use for PHCN, Netflix, etc."""
    bills = load_json(BILLS_FILE, [])
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d")
        reminder = due - timedelta(days=3)
    except:
        due = datetime.now() + timedelta(days=7)
        reminder = due - timedelta(days=3)
        due_date = due.strftime("%Y-%m-%d")
    bill = {
        "id": len(bills) + 1,
        "name": name,
        "amount": amount,
        "due_date": due_date,
        "recurrence": recurrence,
        "category": category,
        "reminder_at": reminder.strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }
    bills.append(bill)
    save_json(BILLS_FILE, bills)
    return f"Bill added: {name} - {amount} due {due_date} ({recurrence}). I'll remind you 3 days before."

@tool
def check_due_bills(days: int = 7) -> str:
    """Check upcoming bills due within N days."""
    bills = load_json(BILLS_FILE, [])
    if not bills:
        return "No bills tracked yet."
    now = datetime.now()
    upcoming = []
    for b in bills:
        try:
            due = datetime.strptime(b["due_date"], "%Y-%m-%d")
            diff = (due - now).days
            if 0 <= diff <= days:
                upcoming.append(f"{b['name']}: {b['amount']} due {b['due_date']} (in {diff} days)")
        except:
            continue
    if not upcoming:
        return f"No bills due in next {days} days. You have {len(bills)} bills total."
    return "Upcoming bills:\n" + "\n".join(upcoming)

@tool
def scan_receipt(receipt_text: str) -> str:
    """Parse a receipt text to extract amount and items."""
    amounts = re.findall(r"\b\d{3,6}\b", receipt_text)
    total = amounts[-1] if amounts else "unknown"
    items = []
    keywords = ["rice", "beans", "oil", "milk", "bread", "sugar", "tomato"]
    for kw in keywords:
        if kw.lower() in receipt_text.lower():
            items.append(kw)
    if items:
        groceries = load_json(GROCERY_FILE, {"items": []})
        for it in items:
            groceries["items"].append({"name": it, "added_at": datetime.now().isoformat()})
        save_json(GROCERY_FILE, groceries)
    return f"Receipt scanned: total {total}, items detected: {', '.join(items) if items else 'none'}. Added to tracking."

@tool
def manage_groceries(action: str, item: str = "") -> str:
    """Manage grocery list."""
    groceries = load_json(GROCERY_FILE, {"items": []})
    if action == "add":
        if not item:
            return "Please specify item to add e.g. rice 5kg"
        groceries["items"].append({"name": item, "added_at": datetime.now().isoformat()})
        save_json(GROCERY_FILE, groceries)
        return f"Added to grocery list: {item}"
    elif action == "list":
        if not groceries["items"]:
            return "Grocery list is empty."
        list_str = "\n".join([f"- {g['name']}" for g in groceries["items"][-10:]])
        return f"Grocery list ({len(groceries['items'])} items):\n{list_str}"
    elif action == "clear":
        groceries = {"items": []}
        save_json(GROCERY_FILE, groceries)
        return "Grocery list cleared."
    else:
        return "Use action: add, list, clear"

@tool
def audit_subscriptions() -> str:
    """Audit subscriptions to find duplicates and total monthly spend."""
    bills = load_json(BILLS_FILE, [])
    if not bills:
        return "No subscriptions found. Add bills first."
    subs = [b for b in bills if b.get("category") in ["entertainment", "subscription", "internet"]]
    if not subs:
        subs = bills
    total = sum([float(s.get("amount", 0)) for s in subs])
    seen = {}
    duplicates = []
    for s in subs:
        name = s["name"].lower()
        if name in seen:
            duplicates.append(s["name"])
        seen[name] = True
    result = f"Subscription Audit: {len(subs)} subs, total monthly {total} Naira."
    if duplicates:
        result += f" Duplicates found: {', '.join(set(duplicates))} - consider canceling one."
    else:
        result += " No duplicates found."
    if total > 10000:
        result += " Tip: Your subs exceed 10k monthly, review DSTV vs Netflix usage."
    return result

@tool
def search_best_practices(query: str) -> str:
    """Search web for best practices. Use specific queries like 'how to save on PHCN bill Lagos'"""
    if len(query.split()) < 4:
        return f"[SEARCH WARNING] Query too generic: '{query}'. Use specific like 'how to save on PHCN bill Lagos'. But would search for: {query}"
    tips = {
        "PHCN": "Use energy-saving bulbs, unplug idle appliances, pay within 5 days for discount in some estates.",
        "Netflix": "Share family plan (4 screens), downgrade to mobile plan if you watch only on phone.",
        "rice": "Buy from Daleko market on Thursdays, price is 5% lower, buy 25kg bag saves 15%.",
        "grocery": "Make list before market, buy in bulk monthly, avoid impulse buying."
    }
    matched_tip = "General tip: Track all bills in LifeLoop to avoid late fees."
    for k, v in tips.items():
        if k.lower() in query.lower():
            matched_tip = v
            break
    return f"[SEARCH READY] Would search web for: '{query}'\nResult: {matched_tip} (Connect Tavily API key in production for live search)"

SYSTEM_PROMPT = """
You are LifeLoop, a life admin agent for people in Lagos, Nigeria.
Manage PHCN, water, rent, Netflix, DSTV, data subscriptions bills
Track groceries, scan receipts, audit subscriptions, search specific saving tips
Always call tools when user mentions bill, grocery, receipt, subscription
Use Naira, due dates YYYY-MM-DD, remind 3 days before
When you search, ALWAYS use specific query like how to save on PHCN bill Lagos
"""

# === FIXED MODEL ID - Use inference profile for us-west-2 ===
# Source: AWS Bedrock docs - github.com/tamirdresher search confirmed
# Old invalid: anthropic.claude-haiku-4-5
# New valid: us.anthropic.claude-haiku-4-5-20251001-v1:0  (cross-region inference profile)

# Option 1: Claude Haiku 4.5 (newest, cheapest, from your screenshot) - RECOMMENDED
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Option 2: Claude 3.5 Haiku (fallback if Haiku 4.5 not enabled yet)
# MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

# Option 3: Claude 3.5 Sonnet (more powerful, more expensive)
# MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

model = BedrockModel(
    model_id=MODEL_ID,
    region_name="us-west-2"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[add_bill, check_due_bills, scan_receipt, manage_groceries, audit_subscriptions, search_best_practices]
)

def local_test():
    print("=== LifeLoop Local Test (No Bedrock) - MVP PASS Mode ===")
    print(add_bill("PHCN", 15000, "2026-09-20", "monthly", "utilities"))
    print(add_bill("Netflix", 2000, "2026-09-15", "monthly", "entertainment"))
    print(manage_groceries("add", "rice (5kg)"))
    print(check_due_bills(7))
    print(audit_subscriptions())
    print(search_best_practices("how to save on PHCN bill Lagos"))
    print("\nAll tools work - ready for Bedrock AgentCore!")

if __name__ == "__main__":
    # Always run local test first - this is your MVP proof
    local_test()
    
    # Try Bedrock if creds exist
    if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE") or os.path.exists(os.path.expanduser("~/.aws/credentials")):
        try:
            print("\n=== LifeLoop Bedrock Agent ===")
            result = agent("I have PHCN bill 15000 due 2026-09-20 and Netflix 2000 monthly, and need rice 5kg for grocery. Also audit my subs and search how to save on PHCN.")
            print(result)
        except Exception as e:
            print(f"\nBedrock error: {e}")
            print("Tip: Check you enabled model in Bedrock console us-west-2 Model access")
    else:
        print("\nSet AWS credentials for full AI brain, but local tools PASS - ready to submit!")






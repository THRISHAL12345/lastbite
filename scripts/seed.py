#!/usr/bin/env python3
"""Load clearly fictional demo tickets through the running API (opt-in)."""
import argparse
import json
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://localhost:8000")
args = parser.parse_args()
base = args.url.rstrip("/")
with urlopen(base + "/api/tickets?limit=1") as response:
    if json.load(response)["total"]:
        raise SystemExit("Queue is not empty; no demo data added.")
tickets = [
    ("VPN access for the design team", "ACCESS", "HIGH", "OPEN", "Alex Morgan", "Sam Lee"),
    ("Meeting room display keeps disconnecting", "HARDWARE", "MEDIUM", "IN_PROGRESS", "Jamie Park", "Jordan Ellis"),
    ("Reset multi-factor authentication", "ACCESS", "URGENT", "OPEN", "Taylor Reed", "Sam Lee"),
    ("Install the new design software", "SOFTWARE", "LOW", "RESOLVED", "Casey Chen", "Morgan Blake"),
    ("Office Wi-Fi is dropping connections", "NETWORK", "HIGH", "IN_PROGRESS", "Riley Quinn", "Jordan Ellis"),
    ("Replace laptop battery", "HARDWARE", "MEDIUM", "OPEN", "Avery Jones", "Unassigned"),
    ("Shared drive permission request", "ACCESS", "LOW", "RESOLVED", "Robin Patel", "Morgan Blake"),
]
for title, category, priority, status, requester, assignee in tickets:
    data = dict(title=title, description="Fictional sample ticket for the RelayDesk capstone demonstration.",
                category=category, priority=priority, status=status, requester=requester, assignee=assignee)
    request = Request(base + "/api/tickets", data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urlopen(request) as response:
        print(f"Created RD-{json.load(response)['id']}: {title}")

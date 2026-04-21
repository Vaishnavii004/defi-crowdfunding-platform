"""
read_campaign.py
----------------
Reads and displays details for all campaigns (or a specific one).
This is a READ-ONLY script — it does NOT send any transaction and costs no gas.

Usage:
    python scripts/read_campaign.py
"""

import time
from config import w3, contract

# Set to a specific campaign ID to view just one, or None to view all
CAMPAIGN_ID = None   # Change to e.g. 0 to view only campaign #0

# ── Helpers ───────────────────────────────────────────────────────────────────

def format_campaign(campaign_id: int) -> dict:
    """Fetch and format one campaign's data for display."""
    creator, goal, deadline, total_raised, withdrawn = \
        contract.functions.getCampaign(campaign_id).call()

    now           = int(time.time())
    is_active     = now < deadline
    goal_reached  = total_raised >= goal
    pct_funded    = (total_raised / goal * 100) if goal > 0 else 0

    deadline_str  = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(deadline))
    status        = "ACTIVE" if is_active else ("SUCCEEDED" if goal_reached else "FAILED")

    return {
        "id"           : campaign_id,
        "creator"      : creator,
        "goal_eth"     : w3.from_wei(goal, "ether"),
        "raised_eth"   : w3.from_wei(total_raised, "ether"),
        "pct_funded"   : round(pct_funded, 1),
        "deadline"     : deadline_str,
        "active"       : is_active,
        "goal_reached" : goal_reached,
        "withdrawn"    : withdrawn,
        "status"       : status,
    }


def print_campaign(data: dict):
    print(f"  Campaign #{data['id']}")
    print(f"  ─────────────────────────────────────")
    print(f"  Creator      : {data['creator']}")
    print(f"  Goal         : {data['goal_eth']} ETH")
    print(f"  Raised       : {data['raised_eth']} ETH  ({data['pct_funded']}%)")
    print(f"  Deadline     : {data['deadline']}")
    print(f"  Status       : {data['status']}")
    print(f"  Withdrawn    : {'Yes' if data['withdrawn'] else 'No'}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    total_campaigns = contract.functions.campaignCount().call()
    print("=" * 52)
    print("  CAMPAIGN DASHBOARD")
    print("=" * 52)
    print(f"  Total campaigns deployed: {total_campaigns}")
    print()

    if total_campaigns == 0:
        print("  No campaigns found. Run create_campaign.py first.")
        return

    if CAMPAIGN_ID is not None:
        # Show just one
        data = format_campaign(CAMPAIGN_ID)
        print_campaign(data)
    else:
        # Show all
        for cid in range(total_campaigns):
            data = format_campaign(cid)
            print_campaign(data)


if __name__ == "__main__":
    main()

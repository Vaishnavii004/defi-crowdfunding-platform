"""
create_campaign.py
------------------
Creates a new crowdfunding campaign on the deployed Crowdfunding contract.

Usage:
    python scripts/create_campaign.py

What it does:
    Calls createCampaign(goal_in_wei, duration_in_seconds) on the contract.
    After the transaction is mined, the campaign is live and contributors
    can start sending ETH to it.
"""

from config import w3, contract, send_transaction, build_tx

# ── Campaign parameters ───────────────────────────────────────────────────────
# Funding goal: 0.01 ETH (good for Sepolia testing — you have limited test ETH)
GOAL_ETH      = 0.01
GOAL_WEI      = w3.to_wei(GOAL_ETH, "ether")

# Duration: 300 seconds = 5 minutes (short so you can test the full flow quickly)
# For a "real" demo use 86400 (1 day) or 604800 (7 days)
DURATION_SECS = 300

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  CREATE CAMPAIGN")
    print("=" * 50)
    print(f"  Goal    : {GOAL_ETH} ETH ({GOAL_WEI} wei)")
    print(f"  Duration: {DURATION_SECS} seconds")
    print()

    tx = contract.functions.createCampaign(
        GOAL_WEI,
        DURATION_SECS
    ).build_transaction(build_tx())

    receipt = send_transaction(tx)

    if receipt["status"] == 1:
        # The new campaign ID = campaignCount before this call.
        # Easiest way: read campaignCount after creation and subtract 1.
        campaign_id = contract.functions.campaignCount().call() - 1
        print(f"\n  Campaign created successfully!")
        print(f"  Campaign ID: {campaign_id}")
        print(f"  Save this ID — you'll need it for contribute/withdraw/refund.")
    else:
        print("\n  Transaction failed. Check your parameters and account balance.")


if __name__ == "__main__":
    main()

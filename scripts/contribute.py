"""
contribute.py
-------------
Sends ETH to an existing crowdfunding campaign.

Usage:
    python scripts/contribute.py

What it does:
    Calls contribute(campaignId) while attaching CONTRIBUTION_ETH worth of ETH.
    The ETH is held in the smart contract until the creator withdraws
    (goal met) or you claim a refund (goal not met after deadline).
"""

from config import w3, contract, send_transaction, build_tx

# ── Parameters ────────────────────────────────────────────────────────────────
# Set this to the campaign ID printed by create_campaign.py
CAMPAIGN_ID      = 0

# How much ETH to contribute (should be > 0 and <= your wallet balance)
CONTRIBUTION_ETH = 0.005
CONTRIBUTION_WEI = w3.to_wei(CONTRIBUTION_ETH, "ether")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  CONTRIBUTE TO CAMPAIGN")
    print("=" * 50)
    print(f"  Campaign ID : {CAMPAIGN_ID}")
    print(f"  Contribution: {CONTRIBUTION_ETH} ETH ({CONTRIBUTION_WEI} wei)")
    print()

    tx = contract.functions.contribute(
        CAMPAIGN_ID
    ).build_transaction(
        build_tx(value_wei=CONTRIBUTION_WEI)  # attach ETH to the transaction
    )

    receipt = send_transaction(tx)

    if receipt["status"] == 1:
        # Read updated campaign state
        creator, goal, deadline, total_raised, withdrawn = \
            contract.functions.getCampaign(CAMPAIGN_ID).call()

        print(f"\n  Contribution recorded!")
        print(f"  Total raised so far : {w3.from_wei(total_raised, 'ether')} ETH")
        print(f"  Funding goal        : {w3.from_wei(goal, 'ether')} ETH")

        if total_raised >= goal:
            print("  Goal REACHED! Creator can now withdraw.")
        else:
            remaining = goal - total_raised
            print(f"  Still needed        : {w3.from_wei(remaining, 'ether')} ETH")
    else:
        print("\n  Transaction failed. Possible reasons:")
        print("  - Campaign deadline has already passed")
        print("  - Campaign ID does not exist")
        print("  - You sent 0 ETH")


if __name__ == "__main__":
    main()

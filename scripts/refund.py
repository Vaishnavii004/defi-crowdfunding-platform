"""
refund.py
---------
Allows a contributor to reclaim their ETH if the campaign failed.

Usage:
    python scripts/refund.py

Requirements:
    - The campaign deadline must have passed
    - The campaign's totalRaised must be < goal (goal was NOT reached)
    - Your wallet (ACCOUNT_ADDRESS in .env) must have contributed to the campaign
    - You must not have already claimed a refund for this campaign
"""

import time
from config import w3, contract, send_transaction, build_tx, ACCOUNT_ADDRESS

# ── Parameters ────────────────────────────────────────────────────────────────
CAMPAIGN_ID = 0   # Set this to the failed campaign

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  CLAIM REFUND")
    print("=" * 50)

    # Read campaign and contribution state
    creator, goal, deadline, total_raised, withdrawn = \
        contract.functions.getCampaign(CAMPAIGN_ID).call()

    my_contribution = contract.functions.getContribution(
        CAMPAIGN_ID, ACCOUNT_ADDRESS
    ).call()

    now = int(time.time())

    print(f"  Campaign ID       : {CAMPAIGN_ID}")
    print(f"  Goal              : {w3.from_wei(goal, 'ether')} ETH")
    print(f"  Total Raised      : {w3.from_wei(total_raised, 'ether')} ETH")
    print(f"  Deadline passed   : {'Yes' if now >= deadline else 'No'}")
    print(f"  Your contribution : {w3.from_wei(my_contribution, 'ether')} ETH")
    print()

    # Pre-flight checks
    if now < deadline:
        remaining = deadline - now
        print(f"  ERROR: Campaign is still active ({remaining} seconds remaining).")
        print("  Refunds are only available after the deadline passes.")
        return

    if total_raised >= goal:
        print("  ERROR: The funding goal was reached — no refunds are issued.")
        print("  The creator can withdraw the funds instead.")
        return

    if my_contribution == 0:
        print("  ERROR: No contribution found for your wallet address.")
        print("  Either you didn't contribute or you've already been refunded.")
        return

    # All checks passed — claim the refund
    tx = contract.functions.refund(CAMPAIGN_ID).build_transaction(build_tx())
    receipt = send_transaction(tx)

    if receipt["status"] == 1:
        print(f"\n  Refund successful!")
        print(f"  {w3.from_wei(my_contribution, 'ether')} ETH returned to {ACCOUNT_ADDRESS}")
    else:
        print("\n  Transaction failed. Check contract state on Etherscan.")


if __name__ == "__main__":
    main()

"""
withdraw.py
-----------
Allows the campaign creator to withdraw funds after the goal is met.

Usage:
    python scripts/withdraw.py

Requirements:
    - You must be the creator of the campaign (same wallet as ACCOUNT_ADDRESS in .env)
    - The campaign's totalRaised must be >= goal
    - withdraw() must not have been called already on this campaign
"""

from config import w3, contract, send_transaction, build_tx, ACCOUNT_ADDRESS

# ── Parameters ────────────────────────────────────────────────────────────────
CAMPAIGN_ID = 0   # Set this to the campaign you created

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  WITHDRAW FUNDS")
    print("=" * 50)

    # Read campaign state before attempting withdrawal
    creator, goal, deadline, total_raised, withdrawn = \
        contract.functions.getCampaign(CAMPAIGN_ID).call()

    print(f"  Campaign ID  : {CAMPAIGN_ID}")
    print(f"  Creator      : {creator}")
    print(f"  Your wallet  : {ACCOUNT_ADDRESS}")
    print(f"  Goal         : {w3.from_wei(goal, 'ether')} ETH")
    print(f"  Total Raised : {w3.from_wei(total_raised, 'ether')} ETH")
    print(f"  Withdrawn    : {'Yes' if withdrawn else 'No'}")
    print()

    # Pre-flight checks (same logic as the contract — fail fast with clear messages)
    if ACCOUNT_ADDRESS.lower() != creator.lower():
        print("  ERROR: Your wallet is not the campaign creator.")
        print(f"  Creator is: {creator}")
        return

    if total_raised < goal:
        print("  ERROR: Funding goal has not been reached yet.")
        print(f"  Still need: {w3.from_wei(goal - total_raised, 'ether')} ETH more.")
        return

    if withdrawn:
        print("  ERROR: Funds were already withdrawn from this campaign.")
        return

    # All checks passed — send the transaction
    tx = contract.functions.withdraw(CAMPAIGN_ID).build_transaction(build_tx())
    receipt = send_transaction(tx)

    if receipt["status"] == 1:
        print(f"\n  Withdrawal successful!")
        print(f"  {w3.from_wei(total_raised, 'ether')} ETH transferred to {creator}")
    else:
        print("\n  Transaction failed. Check contract state on Etherscan.")


if __name__ == "__main__":
    main()

"""
config.py
---------
Shared configuration for all Python Web3 interaction scripts.

HOW TO SET UP:
  1. Copy .env.example to .env
  2. Fill in your RPC_URL, PRIVATE_KEY, and CONTRACT_ADDRESS
  3. Every other script imports from here — change once, applies everywhere.
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load values from the .env file in the project root
load_dotenv()

# ── RPC connection ────────────────────────────────────────────────────────────
# Infura/Alchemy URL for the Sepolia testnet.
# Example: https://sepolia.infura.io/v3/YOUR_PROJECT_ID
RPC_URL = os.getenv("RPC_URL", "")

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise ConnectionError(
        f"Could not connect to Ethereum node at: {RPC_URL}\n"
        "Check that RPC_URL is correct in your .env file."
    )

# ── Wallet ────────────────────────────────────────────────────────────────────
# Your MetaMask account private key (never commit this to GitHub).
# The scripts use this to sign and send transactions.
PRIVATE_KEY     = os.getenv("PRIVATE_KEY", "")
ACCOUNT_ADDRESS = w3.eth.account.from_key(PRIVATE_KEY).address

# ── Contract ──────────────────────────────────────────────────────────────────
# Paste the address Remix gives you after deploying Crowdfunding.sol.
CONTRACT_ADDRESS = w3.to_checksum_address(
    os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
)

# Load the ABI from the abi/ directory.
# After compiling in Remix: Solidity Compiler → ABI button → copy → abi/Crowdfunding_abi.json
ABI_PATH = os.path.join(os.path.dirname(__file__), "..", "abi", "Crowdfunding_abi.json")

with open(ABI_PATH, "r") as f:
    CONTRACT_ABI = json.load(f)

# Create the contract instance — this is what all scripts use to call functions
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# ── Helpers ───────────────────────────────────────────────────────────────────

def send_transaction(tx):
    """
    Sign a transaction with PRIVATE_KEY and broadcast it to the network.
    Returns the transaction receipt once the transaction is mined.

    Usage:
        tx = contract.functions.someFunction(arg).build_transaction({...})
        receipt = send_transaction(tx)
    """
    signed  = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  Tx sent: {tx_hash.hex()}")
    print("  Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    status  = "SUCCESS" if receipt["status"] == 1 else "FAILED"
    print(f"  Status : {status}  (block #{receipt['blockNumber']})")
    return receipt


def build_tx(value_wei=0):
    """
    Returns the common transaction parameters dict.
    Pass value_wei > 0 when sending ETH (e.g. for contribute()).
    """
    return {
        "from":     ACCOUNT_ADDRESS,
        "nonce":    w3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        "gas":      300_000,
        "gasPrice": w3.eth.gas_price,
        "value":    value_wei,
        "chainId":  w3.eth.chain_id,
    }

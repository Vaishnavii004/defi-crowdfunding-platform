# Decentralized Crowdfunding Platform — Project Description

**Course:** BAN 5700 – Blockchain and Cryptocurrency  
**University:** Clark University  
**Team:** Sai Vaishnavi Veeramalla, Neha Naik  

## What It Does

This project implements a DeFi version of Kickstarter on the Ethereum blockchain. Instead of a company holding your money and deciding when to release it, a smart contract enforces all the rules automatically.

**The four rules (enforced in code, not by trust):**
1. A user creates a campaign with a goal (in ETH) and a deadline.
2. Anyone can contribute ETH before the deadline.
3. If the goal is reached → creator can withdraw all funds.
4. If the deadline passes without reaching the goal → every contributor can get a full refund.

## Why Blockchain?

| Traditional Crowdfunding | DeFi Crowdfunding (This Project) |
|---|---|
| Platform controls your money | Smart contract controls money |
| Opaque fee structure | No platform fee |
| Need to trust the company | Rules are code — trustless |
| Creator could disappear with funds | Funds only release on goal met |
| No automatic refunds | Automatic refunds via `refund()` |

## Key Security Properties

- **No double-withdraw:** The `withdrawn` flag is set to `true` before transferring — prevents calling `withdraw()` twice.
- **No double-refund:** `contributions[id][address]` is zeroed before transferring — prevents calling `refund()` twice.
- **Reentrancy protection:** Both `withdraw()` and `refund()` use the "checks-effects-interactions" pattern (state change before ETH transfer).
- **Access control:** Only the campaign creator can call `withdraw()`.

## Tech Stack

| Layer | Technology |
|---|---|
| Smart Contract | Solidity 0.8.20 |
| Development IDE | Remix IDE (remix.ethereum.org) |
| Wallet | MetaMask |
| Test Network | Ethereum Sepolia Testnet |
| Blockchain Interaction | Python + Web3.py |
| Version Control | GitHub |

# Decentralized Crowdfunding Platform (DeFi Kickstarter)

**Course:** BAN 5700 – Blockchain and Cryptocurrency  
**University:** Clark University  
**Team:** Sai Vaishnavi Veeramalla · Neha Naik  

A smart-contract-based crowdfunding dApp built on the Ethereum Sepolia testnet.  
Campaign rules are enforced in Solidity — no intermediary, no trust required.

---

## Repository Structure

```
defi-crowdfunding-platform/
├── contracts/
│   └── Crowdfunding.sol          ← Solidity smart contract (deploy this in Remix)
├── scripts/
│   ├── config.py                 ← Shared Web3 setup (reads .env)
│   ├── create_campaign.py        ← Create a new campaign
│   ├── contribute.py             ← Contribute ETH to a campaign
│   ├── read_campaign.py          ← Read / display campaign details
│   ├── withdraw.py               ← Withdraw funds (creator only, goal met)
│   └── refund.py                 ← Claim refund (contributor, goal not met)
├── abi/
│   └── Crowdfunding_abi.json     ← Contract ABI (update after Remix compile)
├── documentation/
│   └── project_description.md   ← Architecture & design notes
├── .env.example                  ← Template for secrets (copy to .env)
├── .gitignore
└── README.md
```

---

## Prerequisites

| Tool | Purpose | Link |
|---|---|---|
| MetaMask | Ethereum wallet | [metamask.io](https://metamask.io) |
| Remix IDE | Compile & deploy Solidity | [remix.ethereum.org](https://remix.ethereum.org) |
| Infura or Alchemy account | Sepolia RPC endpoint | [infura.io](https://app.infura.io) |
| Python 3.8+ | Run interaction scripts | [python.org](https://python.org) |
| Sepolia test ETH | Pay gas & contribute | [sepoliafaucet.com](https://sepoliafaucet.com) |

---

## Part 1 — Deploy the Smart Contract in Remix

### Step 1: Open Remix
Go to [remix.ethereum.org](https://remix.ethereum.org) in your browser.

### Step 2: Create the contract file
1. In the **File Explorer** panel (left sidebar), click the **+** icon.
2. Name the file `Crowdfunding.sol`.
3. Copy and paste the entire contents of `contracts/Crowdfunding.sol` into the editor.

### Step 3: Compile
1. Click the **Solidity Compiler** tab (shield icon, left sidebar).
2. Set compiler version to **0.8.20** (or any 0.8.x).
3. Click **Compile Crowdfunding.sol**.
4. You should see a green checkmark — no errors.

### Step 4: Get the ABI
1. Below the compile button, click **ABI** (copies to clipboard).
2. Paste it into `abi/Crowdfunding_abi.json` in this repo, replacing the placeholder content.

### Step 5: Deploy to Sepolia
1. Click the **Deploy & Run Transactions** tab (Ethereum icon, left sidebar).
2. Set **Environment** to `Injected Provider - MetaMask`.
3. MetaMask will pop up — connect your wallet and switch to the **Sepolia** network.
4. Under **Contract**, select `Crowdfunding`.
5. Click **Deploy** → confirm the transaction in MetaMask.
6. After the transaction is mined, copy the **contract address** from the Deployed Contracts section.

### Step 6: Save the contract address
Paste the address into your `.env` file as `CONTRACT_ADDRESS`.

---

## Part 2 — Python Web3 Scripts Setup

### Step 1: Install dependencies
```bash
pip install web3 python-dotenv
```

### Step 2: Create your .env file
```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=0xYOUR_METAMASK_PRIVATE_KEY
CONTRACT_ADDRESS=0xYOUR_DEPLOYED_CONTRACT_ADDRESS
```

> **Security note:** Never share or commit your private key. `.env` is in `.gitignore`.

### Step 3: Run the scripts (from the `scripts/` directory)
```bash
cd scripts
```

---

## Part 3 — Running the Full Demo Flow

Run these scripts in order to demonstrate the complete lifecycle of a campaign.

### 1. Create a campaign
```bash
python create_campaign.py
```
Creates a campaign with a 0.01 ETH goal that runs for 5 minutes.  
Note the **Campaign ID** printed in the output (usually `0` for the first one).

### 2. Read campaign details
```bash
python read_campaign.py
```
Shows all campaigns: creator, goal, total raised, deadline, and status.

### 3. Contribute to the campaign
```bash
python contribute.py
```
Sends 0.005 ETH to campaign #0.  
Run this script **twice** (from the same or different wallets) to reach the 0.01 ETH goal.

### 4a. If goal was reached — Withdraw
```bash
python withdraw.py
```
The campaign creator withdraws all raised funds to their wallet.

### 4b. If goal was NOT reached — Refund
```bash
python refund.py
```
Wait for the 5-minute deadline to pass, then each contributor runs this to get their ETH back.

---

## Remix Test Cases (for Testing Without Python)

Use these directly in the Remix **Deploy & Run** panel with the **JavaScript VM** environment for fast local testing (no real ETH needed).

| # | Test | How | Expected Result |
|---|---|---|---|
| 1 | Create a campaign | `createCampaign(1000000000000000000, 300)` — 1 ETH goal, 5 min | Campaign ID 0 created |
| 2 | Contribute before deadline | Set VALUE=0.5 ETH, call `contribute(0)` | totalRaised = 0.5 ETH |
| 3 | Contribute again | Set VALUE=0.5 ETH, call `contribute(0)` | totalRaised = 1 ETH (goal reached) |
| 4 | Contribute after deadline | Wait for deadline, call `contribute(0)` | **Reverts:** "Campaign deadline has passed" |
| 5 | Withdraw by non-creator | Switch to a different account, call `withdraw(0)` | **Reverts:** "Only the campaign creator can withdraw" |
| 6 | Withdraw by creator | Switch back to creator account, call `withdraw(0)` | Success — ETH transferred |
| 7 | Double withdraw | Call `withdraw(0)` again | **Reverts:** "Funds have already been withdrawn" |
| 8 | Create failed campaign | `createCampaign(1000000000000000000, 60)` — set very short duration | New campaign (ID 1) |
| 9 | Contribute to failed campaign | Set VALUE=0.1 ETH, call `contribute(1)` | totalRaised = 0.1 ETH |
| 10 | Refund before deadline | Call `refund(1)` immediately | **Reverts:** "Campaign is still active" |
| 11 | Refund after deadline | Wait for deadline, call `refund(1)` | Success — ETH returned |
| 12 | Double refund | Call `refund(1)` again | **Reverts:** "No contribution found for this address" |
| 13 | Refund when goal met | Create campaign, meet the goal, call `refund()` | **Reverts:** "Goal was reached; no refunds available" |

---

## Smart Contract — Function Reference

```
createCampaign(uint256 _goal, uint256 _duration)
    Creates a new campaign. _goal is in wei. _duration is seconds from now.

contribute(uint256 _campaignId)  [payable]
    Send ETH to campaign. Attach ETH in the VALUE field.

withdraw(uint256 _campaignId)
    Creator only. Withdraws all raised ETH if goal is met.

refund(uint256 _campaignId)
    Contributor only. Returns their ETH if goal was not met after deadline.

getCampaign(uint256 _campaignId)  [view]
    Returns: creator, goal, deadline, totalRaised, withdrawn.

getContribution(uint256 _campaignId, address _contributor)  [view]
    Returns how much a specific address contributed (in wei).
```

---

## Verify on Etherscan

After deploying to Sepolia, paste your contract address into:  
`https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS`

You can see all transactions, events, and call the contract directly from Etherscan.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Could not connect to Ethereum node` | Check `RPC_URL` in `.env` is correct and Infura key is active |
| `Transaction failed` in Python | Check wallet has Sepolia ETH for gas fees |
| `Only the campaign creator can withdraw` | `PRIVATE_KEY` in `.env` must match the account that called `createCampaign` |
| `Campaign is still active` (refund) | Wait for the deadline to pass before calling `refund.py` |
| Remix shows wrong contract | Make sure the ABI in `abi/Crowdfunding_abi.json` matches the compiled version |

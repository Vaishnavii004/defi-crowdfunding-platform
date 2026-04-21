// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title  Crowdfunding
 * @notice Decentralized Crowdfunding Platform (DeFi Kickstarter)
 *         Course: BAN 5700 – Blockchain and Cryptocurrency
 *         University: Clark University
 *         Team: Sai Vaishnavi Veeramalla, Neha Naik
 *
 * HOW IT WORKS (plain English):
 *   1. Anyone can create a campaign with a funding goal and duration.
 *   2. Anyone can contribute ETH to a campaign BEFORE its deadline.
 *   3. AFTER the deadline, if the goal was reached, the creator can withdraw.
 *   4. AFTER the deadline, if the goal was NOT reached, each contributor
 *      can claim a full refund of exactly what they sent.
 */
contract Crowdfunding {

    // =========================================================
    //  DATA STRUCTURES
    // =========================================================

    /**
     * Campaign – stores everything about one crowdfunding campaign.
     *
     * creator     The wallet address of whoever called createCampaign().
     *             Only this address is allowed to call withdraw().
     *
     * goal        The funding target measured in wei.
     *             (1 ETH = 1,000,000,000,000,000,000 wei)
     *             The creator can only withdraw once totalRaised >= goal.
     *
     * deadline    Unix timestamp (seconds since Jan 1 1970) when the
     *             campaign ends. Contributions are rejected after this.
     *             Refunds are only available after this timestamp if the
     *             goal was not met.
     *
     * totalRaised Running sum of all ETH sent to this campaign (in wei).
     *
     * withdrawn   Boolean flag. Set to true after a successful withdraw().
     *             Guards against calling withdraw() twice on the same campaign.
     */
    struct Campaign {
        address payable creator;
        uint256 goal;
        uint256 deadline;
        uint256 totalRaised;
        bool    withdrawn;
    }

    // =========================================================
    //  STATE VARIABLES
    // =========================================================

    /**
     * campaignCount – total number of campaigns ever created.
     * Also used as the next campaign ID (IDs start at 0).
     * After createCampaign() is called once: campaignCount = 1, campaign ID = 0.
     */
    uint256 public campaignCount;

    /**
     * campaigns – maps a campaign ID to its Campaign struct.
     * Example: campaigns[0] returns the very first campaign.
     */
    mapping(uint256 => Campaign) public campaigns;

    /**
     * contributions – nested mapping: campaignId => contributor address => amount (wei).
     * Tracks exactly how much each address contributed to each campaign.
     * Used to calculate refund amounts and to prevent double-refunds.
     * Example: contributions[0][0xABC...] = 500000000000000000  (0.5 ETH)
     */
    mapping(uint256 => mapping(address => uint256)) public contributions;

    // =========================================================
    //  EVENTS
    // =========================================================
    //
    // Events are permanent log entries on the blockchain.
    // They cost very little gas and are readable by Web3.py scripts
    // and blockchain explorers like Etherscan.

    event CampaignCreated(
        uint256 indexed campaignId,
        address indexed creator,
        uint256 goal,
        uint256 deadline
    );

    event ContributionMade(
        uint256 indexed campaignId,
        address indexed contributor,
        uint256 amount
    );

    event WithdrawalMade(
        uint256 indexed campaignId,
        address indexed creator,
        uint256 amount
    );

    event RefundIssued(
        uint256 indexed campaignId,
        address indexed contributor,
        uint256 amount
    );

    // =========================================================
    //  WRITE FUNCTIONS  (cost gas – change blockchain state)
    // =========================================================

    /**
     * createCampaign
     * --------------
     * Lets any user start a new crowdfunding campaign.
     *
     * @param _goal      Funding target in wei. Must be > 0.
     *                   In Remix you can type: 1000000000000000000 for 1 ETH.
     * @param _duration  How many SECONDS the campaign should run.
     *                   Examples:
     *                     300     = 5 minutes  (useful for quick Remix tests)
     *                     86400   = 1 day
     *                     604800  = 7 days
     *
     * NOTE: We accept _duration (seconds from now) rather than a raw timestamp
     * so it is easy to test in Remix without calculating future timestamps.
     *
     * After a successful call the new campaign is stored at:
     *   campaigns[campaignCount - 1]
     */
    function createCampaign(uint256 _goal, uint256 _duration) external {
        require(_goal > 0,     "Goal must be greater than zero");
        require(_duration > 0, "Duration must be greater than zero");

        uint256 campaignId = campaignCount; // save current ID before incrementing

        campaigns[campaignId] = Campaign({
            creator:     payable(msg.sender),
            goal:        _goal,
            deadline:    block.timestamp + _duration,
            totalRaised: 0,
            withdrawn:   false
        });

        campaignCount++;

        emit CampaignCreated(campaignId, msg.sender, _goal, block.timestamp + _duration);
    }

    /**
     * contribute
     * ----------
     * Lets any address send ETH to support a campaign.
     * The ETH is locked inside this contract until:
     *   (a) the creator withdraws after goal is met, OR
     *   (b) the contributor claims a refund after a failed campaign.
     *
     * @param _campaignId  The numeric ID of the campaign to fund.
     *
     * In Remix: set the VALUE field (e.g. 0.1 ETH) before clicking contribute.
     * msg.value is the ETH amount the caller attaches to the transaction.
     */
    function contribute(uint256 _campaignId) external payable {
        Campaign storage c = campaigns[_campaignId];

        // A deadline of 0 means the campaign was never created.
        require(c.deadline != 0, "Campaign does not exist");

        // No contributions after the deadline.
        require(block.timestamp < c.deadline, "Campaign deadline has passed");

        // Caller must attach some ETH to the transaction.
        require(msg.value > 0, "Contribution must be greater than zero");

        // Defence-in-depth: with the new rule that withdraw() requires the deadline
        // to have passed, this check is logically unreachable (contributing after
        // deadline is already blocked above). Kept as an explicit safety net.
        require(!c.withdrawn, "Campaign has already been completed and withdrawn");

        c.totalRaised                          += msg.value;
        contributions[_campaignId][msg.sender] += msg.value;

        emit ContributionMade(_campaignId, msg.sender, msg.value);
    }

    /**
     * withdraw
     * --------
     * Lets the campaign creator collect all raised funds.
     *
     * Business rules:
     *   1. Campaign must exist.
     *   2. Only the creator can call this function.
     *   3. The deadline must have passed — the campaign window must be closed
     *      before anyone can touch the funds.
     *   4. The total raised must be >= the goal.
     *   5. Can only be called once (withdrawn flag prevents double-withdraw).
     *
     * ETH transfer:
     *   Uses a low-level call instead of transfer(). transfer() hard-caps the
     *   forwarded gas at 2300, which can silently fail if the recipient is a
     *   smart contract with a non-trivial fallback function. call() forwards
     *   enough gas for the recipient to execute and we explicitly require
     *   success, so a failed transfer always reverts.
     *
     * IMPORTANT: We set withdrawn = true BEFORE transferring ETH.
     * This pattern (called "checks-effects-interactions") prevents a
     * re-entrancy attack where a malicious contract could call withdraw()
     * again during the ETH transfer.
     *
     * @param _campaignId  The ID of the campaign to withdraw from.
     */
    function withdraw(uint256 _campaignId) external {
        Campaign storage c = campaigns[_campaignId];

        require(c.deadline != 0,               "Campaign does not exist");
        require(msg.sender == c.creator,       "Only the campaign creator can withdraw");
        require(block.timestamp >= c.deadline, "Campaign deadline has not passed yet");
        require(c.totalRaised >= c.goal,       "Funding goal not reached");
        require(!c.withdrawn,                  "Funds have already been withdrawn");

        // --- Effects (state changes first) ---
        c.withdrawn = true;
        uint256 amount = c.totalRaised;

        // --- Interaction (low-level call — no gas cap, explicit success check) ---
        (bool success, ) = c.creator.call{value: amount}("");
        require(success, "Withdraw transfer failed");

        emit WithdrawalMade(_campaignId, msg.sender, amount);
    }

    /**
     * refund
     * ------
     * Lets a contributor reclaim their ETH if the campaign failed.
     *
     * Business rules:
     *   1. Campaign must exist.
     *   2. The deadline must have passed — the campaign window must be closed.
     *   3. The funding goal must NOT have been reached.
     *   4. The caller must have contributed a non-zero amount.
     *   5. Sets contribution to 0 BEFORE transferring (prevents double-refund).
     *
     * ETH transfer:
     *   Uses a low-level call instead of transfer() for the same reason as
     *   withdraw() — no 2300-gas cap, explicit success check, always reverts
     *   on failure.
     *
     * @param _campaignId  The ID of the failed campaign.
     */
    function refund(uint256 _campaignId) external {
        Campaign storage c = campaigns[_campaignId];

        require(c.deadline != 0,               "Campaign does not exist");
        require(block.timestamp >= c.deadline, "Campaign is still active");
        require(c.totalRaised < c.goal,        "Goal was reached; no refunds available");

        uint256 contributed = contributions[_campaignId][msg.sender];
        require(contributed > 0, "No contribution found for this address");

        // --- Effects (zero out before sending to prevent double-refund) ---
        contributions[_campaignId][msg.sender] = 0;

        // --- Interaction (low-level call — no gas cap, explicit success check) ---
        (bool success, ) = payable(msg.sender).call{value: contributed}("");
        require(success, "Refund transfer failed");

        emit RefundIssued(_campaignId, msg.sender, contributed);
    }

    // =========================================================
    //  READ / VIEW FUNCTIONS  (free – no gas cost)
    // =========================================================

    /**
     * getCampaign
     * -----------
     * Returns all stored details for a single campaign.
     * Useful for front-ends and Python scripts.
     *
     * @param  _campaignId  The campaign ID to look up.
     * @return creator      Address of the campaign creator.
     * @return goal         Funding target in wei.
     * @return deadline     Unix timestamp when the campaign ends.
     * @return totalRaised  Total ETH raised so far in wei.
     * @return withdrawn    True if the creator has already withdrawn.
     */
    function getCampaign(uint256 _campaignId)
        external
        view
        returns (
            address creator,
            uint256 goal,
            uint256 deadline,
            uint256 totalRaised,
            bool    withdrawn
        )
    {
        Campaign storage c = campaigns[_campaignId];
        return (c.creator, c.goal, c.deadline, c.totalRaised, c.withdrawn);
    }

    /**
     * getContribution
     * ---------------
     * Returns how much a specific address contributed to a campaign (in wei).
     *
     * @param _campaignId   The campaign ID.
     * @param _contributor  The wallet address to query.
     * @return              Amount contributed in wei (0 if none or refunded).
     */
    function getContribution(uint256 _campaignId, address _contributor)
        external
        view
        returns (uint256)
    {
        return contributions[_campaignId][_contributor];
    }
}

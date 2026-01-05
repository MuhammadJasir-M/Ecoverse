// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IProcurementEvents
 * @dev Interface defining events for procurement audit transparency
 */
interface IProcurementEvents {
    
    event TenderCreated(
        uint256 indexed tenderId,
        bytes32 dataHash,
        uint256 timestamp,
        address creator
    );
    
    event BidSubmitted(
        uint256 indexed bidId,
        uint256 indexed tenderId,
        bytes32 dataHash,
        uint256 timestamp,
        address submitter
    );
    
    event AwardDecided(
        uint256 indexed tenderId,
        uint256 indexed winningBidId,
        bytes32 dataHash,
        uint256 timestamp,
        address awarder
    );
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IProcurementStructs
 * @dev Interface defining data structures for procurement audit
 */
interface IProcurementStructs {
    
    struct TenderLog {
        uint256 timestamp;
        bytes32 dataHash;
        address creator;
    }
    
    struct BidLog {
        uint256 timestamp;
        bytes32 dataHash;
        address submitter;
    }
    
    struct AwardLog {
        uint256 timestamp;
        uint256 winningBidId;
        bytes32 dataHash;
        address awarder;
    }
}

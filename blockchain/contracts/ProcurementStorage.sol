// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProcurementStorage
 * @dev Abstract contract managing storage for procurement audit
 */
abstract contract ProcurementStorage {
    
    // Import structures
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
    
    // Storage mappings
    mapping(uint256 => TenderLog) internal tenderLogs;
    mapping(uint256 => mapping(uint256 => BidLog)) internal bidLogs; // tenderId => bidId => BidLog
    mapping(uint256 => uint256) internal bidCounts; // tenderId => count
    mapping(uint256 => AwardLog) internal awardLogs;
}

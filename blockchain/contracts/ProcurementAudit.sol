// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProcurementAudit
 * @dev Immutable audit trail for government procurement transparency
 * @notice This contract stores only hashes and timestamps - no sensitive data
 */
contract ProcurementAudit {
    
    // Structures
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
    mapping(uint256 => TenderLog) public tenderLogs;
    mapping(uint256 => mapping(uint256 => BidLog)) public bidLogs; // tenderId => bidId => BidLog
    mapping(uint256 => uint256) public bidCounts; // tenderId => count
    mapping(uint256 => AwardLog) public awardLogs;
    
    // Events for transparency
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
    
    // Modifiers
    modifier tenderExists(uint256 _tenderId) {
        require(tenderLogs[_tenderId].timestamp > 0, "Tender does not exist");
        _;
    }
    
    modifier tenderNotAwarded(uint256 _tenderId) {
        require(awardLogs[_tenderId].timestamp == 0, "Tender already awarded");
        _;
    }
    
    /**
     * @dev Log tender creation on blockchain
     * @param _tenderId Unique tender identifier from database
     * @param _dataHash SHA-256 hash of tender data
     */
    function logTenderCreation(
        uint256 _tenderId,
        bytes32 _dataHash
    ) external {
        require(tenderLogs[_tenderId].timestamp == 0, "Tender already exists");
        require(_dataHash != bytes32(0), "Invalid data hash");
        
        tenderLogs[_tenderId] = TenderLog({
            timestamp: block.timestamp,
            dataHash: _dataHash,
            creator: msg.sender
        });
        
        emit TenderCreated(_tenderId, _dataHash, block.timestamp, msg.sender);
    }
    
    /**
     * @dev Log bid submission on blockchain
     * @param _bidId Unique bid identifier from database
     * @param _tenderId Associated tender ID
     * @param _dataHash SHA-256 hash of bid data
     */
    function logBidSubmission(
        uint256 _bidId,
        uint256 _tenderId,
        bytes32 _dataHash
    ) external tenderExists(_tenderId) tenderNotAwarded(_tenderId) {
        require(_dataHash != bytes32(0), "Invalid data hash");
        require(bidLogs[_tenderId][_bidId].timestamp == 0, "Bid already exists");
        
        bidLogs[_tenderId][_bidId] = BidLog({
            timestamp: block.timestamp,
            dataHash: _dataHash,
            submitter: msg.sender
        });
        
        bidCounts[_tenderId]++;
        
        emit BidSubmitted(_bidId, _tenderId, _dataHash, block.timestamp, msg.sender);
    }
    
    /**
     * @dev Log award decision on blockchain
     * @param _tenderId Tender being awarded
     * @param _winningBidId Winning bid identifier
     * @param _dataHash SHA-256 hash of award decision
     */
    function logAwardDecision(
        uint256 _tenderId,
        uint256 _winningBidId,
        bytes32 _dataHash
    ) external tenderExists(_tenderId) tenderNotAwarded(_tenderId) {
        require(_dataHash != bytes32(0), "Invalid data hash");
        require(bidLogs[_tenderId][_winningBidId].timestamp > 0, "Winning bid does not exist");
        
        awardLogs[_tenderId] = AwardLog({
            timestamp: block.timestamp,
            winningBidId: _winningBidId,
            dataHash: _dataHash,
            awarder: msg.sender
        });
        
        emit AwardDecided(_tenderId, _winningBidId, _dataHash, block.timestamp, msg.sender);
    }
    
    // View functions for transparency
    
    /**
     * @dev Get tender creation log
     */
    function getTenderLog(uint256 _tenderId) 
        external 
        view 
        returns (uint256 timestamp, bytes32 dataHash) 
    {
        TenderLog memory log = tenderLogs[_tenderId];
        return (log.timestamp, log.dataHash);
    }
    
    /**
     * @dev Get bid submission log
     */
    function getBidLog(uint256 _tenderId, uint256 _bidId)
        external
        view
        returns (uint256 timestamp, bytes32 dataHash)
    {
        BidLog memory log = bidLogs[_tenderId][_bidId];
        return (log.timestamp, log.dataHash);
    }
    
    /**
     * @dev Get total number of bids for a tender
     */
    function getBidCount(uint256 _tenderId) external view returns (uint256) {
        return bidCounts[_tenderId];
    }
    
    /**
     * @dev Get award decision log
     */
    function getAwardLog(uint256 _tenderId)
        external
        view
        returns (uint256 timestamp, uint256 winningBidId)
    {
        AwardLog memory log = awardLogs[_tenderId];
        return (log.timestamp, log.winningBidId);
    }
    
    /**
     * @dev Verify complete audit trail for a tender
     * @param _tenderId The tender ID to verify
     * @return tenderVerified Whether tender is verified on blockchain
     * @return bidCount Number of bids submitted
     * @return awardVerified Whether award decision is verified
     */
    function verifyAuditTrail(uint256 _tenderId)
        external
        view
        returns (bool tenderVerified, uint256 bidCount, bool awardVerified)
    {
        tenderVerified = tenderLogs[_tenderId].timestamp > 0;
        bidCount = bidCounts[_tenderId];
        awardVerified = awardLogs[_tenderId].timestamp > 0;
    }
}
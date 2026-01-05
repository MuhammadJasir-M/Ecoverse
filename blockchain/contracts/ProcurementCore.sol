// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ProcurementModifiers.sol";
import "./IProcurementEvents.sol";

/**
 * @title ProcurementCore
 * @dev Core contract implementing procurement logging functionality
 */
abstract contract ProcurementCore is ProcurementModifiers, IProcurementEvents {
    
    /**
     * @dev Log tender creation on blockchain
     * @param _tenderId Unique tender identifier from database
     * @param _dataHash SHA-256 hash of tender data
     */
    function logTenderCreation(
        uint256 _tenderId,
        bytes32 _dataHash
    ) external validHash(_dataHash) {
        require(tenderLogs[_tenderId].timestamp == 0, "Tender already exists");
        
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
    ) external tenderExists(_tenderId) tenderNotAwarded(_tenderId) validHash(_dataHash) {
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
    ) external tenderExists(_tenderId) tenderNotAwarded(_tenderId) validHash(_dataHash) {
        require(bidLogs[_tenderId][_winningBidId].timestamp > 0, "Winning bid does not exist");
        
        awardLogs[_tenderId] = AwardLog({
            timestamp: block.timestamp,
            winningBidId: _winningBidId,
            dataHash: _dataHash,
            awarder: msg.sender
        });
        
        emit AwardDecided(_tenderId, _winningBidId, _dataHash, block.timestamp, msg.sender);
    }
}

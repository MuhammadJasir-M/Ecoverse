// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ProcurementStorage.sol";

/**
 * @title ProcurementView
 * @dev View functions for querying procurement audit data
 */
abstract contract ProcurementView is ProcurementStorage {
    
    /**
     * @dev Get tender creation log
     * @param _tenderId The tender ID to query
     * @return timestamp When the tender was created
     * @return dataHash Hash of the tender data
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
     * @param _tenderId The tender ID
     * @param _bidId The bid ID
     * @return timestamp When the bid was submitted
     * @return dataHash Hash of the bid data
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
     * @param _tenderId The tender ID
     * @return count Total number of bids submitted
     */
    function getBidCount(uint256 _tenderId) 
        external 
        view 
        returns (uint256 count) 
    {
        return bidCounts[_tenderId];
    }
    
    /**
     * @dev Get award decision log
     * @param _tenderId The tender ID
     * @return timestamp When the award was decided
     * @return winningBidId The ID of the winning bid
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
    
    /**
     * @dev Get complete tender information
     * @param _tenderId The tender ID
     * @return timestamp When tender was created
     * @return dataHash Hash of tender data
     * @return creator Address that created the tender
     */
    function getTenderDetails(uint256 _tenderId)
        external
        view
        returns (uint256 timestamp, bytes32 dataHash, address creator)
    {
        TenderLog memory log = tenderLogs[_tenderId];
        return (log.timestamp, log.dataHash, log.creator);
    }
    
    /**
     * @dev Get complete award information
     * @param _tenderId The tender ID
     * @return timestamp When award was decided
     * @return winningBidId The winning bid ID
     * @return dataHash Hash of award data
     * @return awarder Address that made the award decision
     */
    function getAwardDetails(uint256 _tenderId)
        external
        view
        returns (
            uint256 timestamp, 
            uint256 winningBidId, 
            bytes32 dataHash, 
            address awarder
        )
    {
        AwardLog memory log = awardLogs[_tenderId];
        return (log.timestamp, log.winningBidId, log.dataHash, log.awarder);
    }
}

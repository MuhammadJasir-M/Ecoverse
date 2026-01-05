// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ProcurementStorage.sol";

/**
 * @title ProcurementModifiers
 * @dev Contract containing modifiers for procurement operations
 */
abstract contract ProcurementModifiers is ProcurementStorage {
    
    /**
     * @dev Ensures tender exists in the system
     */
    modifier tenderExists(uint256 _tenderId) {
        require(tenderLogs[_tenderId].timestamp > 0, "Tender does not exist");
        _;
    }
    
    /**
     * @dev Ensures tender has not been awarded yet
     */
    modifier tenderNotAwarded(uint256 _tenderId) {
        require(awardLogs[_tenderId].timestamp == 0, "Tender already awarded");
        _;
    }
    
    /**
     * @dev Validates data hash is not empty
     */
    modifier validHash(bytes32 _dataHash) {
        require(_dataHash != bytes32(0), "Invalid data hash");
        _;
    }
}

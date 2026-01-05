from web3 import Web3
from app.config import get_settings
import json

settings = get_settings()

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_RPC_URL))
        self.account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
        
        # Load contract ABI
        with open('/app/app/services/ProcurementAudit_ABI.json', 'r') as f:
            self.contract_abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=settings.CONTRACT_ADDRESS,
            abi=self.contract_abi
        )
    
    def log_tender_creation(self, tender_id: int, data_hash: str) -> str:
        """Log tender creation on blockchain"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = self.contract.functions.logTenderCreation(
                tender_id,
                data_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.transactionHash.hex()
        except Exception as e:
            print(f"Blockchain error: {e}")
            return None
    
    def log_bid_submission(self, bid_id: int, tender_id: int, data_hash: str) -> str:
        """Log bid submission on blockchain"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = self.contract.functions.logBidSubmission(
                bid_id,
                tender_id,
                data_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.transactionHash.hex()
        except Exception as e:
            print(f"Blockchain error: {e}")
            return None
    
    def log_award_decision(self, tender_id: int, winning_bid_id: int, data_hash: str) -> str:
        """Log award decision on blockchain"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = self.contract.functions.logAwardDecision(
                tender_id,
                winning_bid_id,
                data_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.transactionHash.hex()
        except Exception as e:
            print(f"Blockchain error: {e}")
            return None
    
    def verify_audit_trail(self, tender_id: int) -> dict:
        """Verify complete audit trail for a tender"""
        try:
            tender_log = self.contract.functions.getTenderLog(tender_id).call()
            bid_count = self.contract.functions.getBidCount(tender_id).call()
            award_log = self.contract.functions.getAwardLog(tender_id).call()
            
            # Convert bytes to hex strings for JSON serialization
            tender_hash = tender_log[1].hex() if isinstance(tender_log[1], bytes) else tender_log[1]
            
            return {
                "tender_verified": tender_log[0] > 0,
                "tender_timestamp": tender_log[0],
                "tender_hash": tender_hash,
                "total_bids": bid_count,
                "award_verified": award_log[0] > 0,
                "award_timestamp": award_log[0],
                "winning_bid_id": award_log[1]
            }
        except Exception as e:
            print(f"Verification error: {e}")
            return None

import logging, sys, time, hashlib, json
from ecdsa import NIST256p, VerifyingKey

from .utils import sorted_dict_by_key, pprint

MINING_DIFFICULTY = 3 # necessary when guiding nonce(first 3 digits are 0)
MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARD = 1.0 # mining reward

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


class BlockChain(object):

    def __init__(self, blockchain_address=None):

        # temporarily store
        self.transaction_pool = []
        # place of block
        self.chain = []
        # first pre block is empty(={})
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address


    def create_block(self, nonce, previous_hash):

        block = {
            'nonce': nonce,
            'previous_hash': previous_hash,
            'transactions': self.transaction_pool,
            'timestamp': time.time()
        }

        block = utils.sorted_dict_by_key(block)

        self.chain.append(block)
        # init pool
        self.transaction_pool = []
        return block

    # create hash from pre block
    def hash(self, pre_block):

        sorted_block = json.dumps(pre_block, sort_keys=True)
        hash = hashlib.sha256(sorted_block.encode()).hexdigest()
        return hash


    # add transaction to pool
    def add_transaction(self, sender_address, recipient_address, value, sender_public_key=None, signature=None):

        transaction = {
            'sender_address': sender_address,
            'recipient_address': recipient_address,
            'value': value
        }
        transaction = utils.sorted_dict_by_key(transaction)

        if sender_address == MINING_SENDER:
            self.transaction_pool.append(transaction)
            return True

        # トランザクション検証がTrueで実行
        if self.verify_transactions_signature(sender_public_key, signature, transaction):

            self.transaction_pool.append(transaction)
            return True
        return False

    # Nodeでのトランザクション検証処理
    def verify_transactions_signature(self, sender_public_key, signature, transaction):

        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode('utf-8'))
        message =sha256.digest()
        signature_bytes = bytes().fromhex(signature)
        verifying_key = VerifyingKey.from_string(bytes().fromhex(sender_public_key), curve=NIST256p)
        verified_key = verifying_key.verify(signature_bytes, message)

        return verified_key


    # calculate nance
    def valid_proof(self, transactions, previous_hash, nonce, difficulty=MINING_DIFFICULTY):

        guess_block = {
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }
        guess_block = utils.sorted_dict_by_key(guess_block)
        guess_hash = self.hash(guess_block)
        return guess_hash[:difficulty] == '0'*difficulty


    def proof_of_work(self):

        transactions = self.transaction_pool.copy()
        previous_hash = self.hash(self.chain[-1])

        # find solution
        nonce = 0
        while self.valid_proof(transactions, previous_hash, nonce) is False:
            nonce += 1
            return nonce


    # マイニング？
    def mining(self):
        self.add_transaction(
            sender_address=MINING_SENDER,
            recipient_address=self.blockchain_address,
            value=MINING_REWARD
        )
        nonce = self.proof_of_work()
        previous_hash = self.hash(self.chain[-1])
        self.create_block(nonce, previous_hash)

        logger.info({'action': 'mining', 'status': 'success'})

        return True


    def calculate_total_amount(self, blockchain_address):

        total_amount = 0.0

        for block in self.chain:
            for transaction in block['transactions']:
                value = float(transaction['value'])

                if blockchain_address == transaction['recipient_address']:
                    total_amount += value
                if blockchain_address == transaction['sender_address']:
                    total_amount += value
        return total_amount

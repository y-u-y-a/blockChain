import base58, codecs, hashlib
from ecdsa import NIST256p, SigningKey

from .utils import sorted_dict_by_key, pprint


class Wallet(object):

    def __init__(self):
        self._private_key = SigningKey.generate(curve=NIST256p)
        self._public_key = self._private_key.get_verifying_key()
        self._blockchain_address = self.generate_blockchain_address()

    # decorate？
    @property
    def private_key(self):
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        return self._public_key.to_string().hex()

    @property
    def blockchain_address(self):
        return self._blockchain_address


    # Don't understand
    def generate_blockchain_address(self):
        # 2
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        # 3
        ripemed160_bpk = hashlib.new('ripemd160')
        ripemed160_bpk.update(sha256_bpk_digest)
        ripemed160_bpk_digest = ripemed160_bpk.digest()
        ripemed160_bpk_hex = codecs.encode(ripemed160_bpk_digest, 'hex')
        #4
        network_byte = b'00'
        network_bitcoin_public_key = network_byte + ripemed160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(
            network_bitcoin_public_key, 'hex')
        #5
        sha256_bpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_bpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        #6
        checksum = sha256_hex[:8]
        #7
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        #8
        blockchain_address = base58.b58encode(address_hex).decode('utf-8')
        return blockchain_address


class Transaction(object):

    def __init__(self, sender_private_key, sender_public_key, sender_address, recipient_address, value):

        self.sender_private_key = sender_private_key
        self.sender_public_key = sender_public_key
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.value = value

    def generate_signature(self):
        sha256 = hashlib.sha256()
        transaction = {
            'sender_address': self.sender_address,
            'recipient_address': self.recipient_address,
            'value': float(self.value)
        }
        transaction = sorted_dict_by_key(transaction)

        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()
        private_key = SigningKey.from_string(
            bytes().fromhex(self.sender_private_key), curve=NIST256p)
        private_key_sign = private_key.sign(message)
        signature = private_key_sign.hex()

        return signature




if __name__ == '__main__':
    wallet_M = Wallet()
    wallet_A = Wallet()
    wallet_B = Wallet()

    # generate transaction content
    t = Transaction(
        wallet_A.private_key, wallet_A.public_key, wallet_A.blockchain_address, wallet_B.blockchain_address, 1.0)


# BlockChain Node ################

from .blockchain import BlockChain

block_chain = BlockChain(blockchain_address=wallet_M.blockchain_address)

is_added = block_chain.add_transaction(
    wallet_A.blockchain_address,
    wallet_B.blockchain_address,
    1.0,
    wallet_A.public_key,
    t.generate_signature()
)

print('Added?', is_added)
block_chain.mining()
pprint(block_chain.chain)

print('A', block_chain.calculate_total_amount(wallet_A.blockchain_address))
print('B', block_chain.calculate_total_amount(wallet_B.blockchain_address))

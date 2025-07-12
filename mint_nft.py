from web3 import Web3
from web3.middleware.poa import geth_poa_middleware
import json
import os
import secrets

# === Constants ===
AVALANCHE_RPC = "https://api.avax-test.network/ext/bc/C/rpc"
NFT_CONTRACT_ADDRESS = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
ABI_PATH = "NFT.abi"  # Path to your ABI file
PRIVATE_KEY = "0x1ffdb27a9756f077df3cf6746add67708e778e7ba6f2fe1be05d51cba4f03537"

# === Connect to Avalanche Fuji Testnet ===
w3 = Web3(Web3.HTTPProvider(AVALANCHE_RPC))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
assert w3.is_connected(), "Failed to connect to Avalanche Fuji Testnet"

# === Load ABI and Contract ===
with open(ABI_PATH, "r") as f:
    abi = json.load(f)
contract = w3.eth.contract(address=NFT_CONTRACT_ADDRESS, abi=abi)

# === Get your wallet address ===
account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address
print("Using account:", address)

# === Prepare transaction to claim an NFT ===
nonce = secrets.token_bytes(32)  # random 32-byte nonce
print("Generated nonce:", nonce.hex())

# Estimate gas and build transaction
tx = contract.functions.claim(nonce).build_transaction({
    'from': address,
    'nonce': w3.eth.get_transaction_count(address),
    'gas': 300000,  # estimate generously
    'gasPrice': w3.eth.gas_price,
    'chainId': 43113  # Fuji testnet chain ID
})

# Sign and send transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("Transaction sent! Hash:", tx_hash.hex())

# Wait for confirmation
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Transaction confirmed in block:", receipt.blockNumber)

from flask import Flask, request, jsonify
from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Connect to Ethereum network (Holesky testnet)
w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_NODE_URL')))
w3.eth.default_chain_id = int(os.getenv('CHAIN_ID', '17000'))  # Holesky chain ID

# Contract ABI and address
contract_address = os.getenv('CONTRACT_ADDRESS')
contract_abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "_issuerName", "type": "string"},
            {"internalType": "string", "name": "_receiverName", "type": "string"},
            {"internalType": "string", "name": "_courseName", "type": "string"},
            {"internalType": "string", "name": "_department", "type": "string"},
            {"internalType": "uint256", "name": "_expiryDate", "type": "uint256"}
        ],
        "name": "issueCertificate",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "_certificateId", "type": "bytes32"}],
        "name": "validateCertificate",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"},
            {
                "components": [
                    {"internalType": "string", "name": "issuerName", "type": "string"},
                    {"internalType": "string", "name": "receiverName", "type": "string"},
                    {"internalType": "string", "name": "courseName", "type": "string"},
                    {"internalType": "string", "name": "department", "type": "string"},
                    {"internalType": "uint256", "name": "issuedDate", "type": "uint256"},
                    {"internalType": "uint256", "name": "expiryDate", "type": "uint256"},
                    {"internalType": "bool", "name": "isValid", "type": "bool"}
                ],
                "internalType": "struct CertificateSystem.Certificate",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "bytes32", "name": "certificateId", "type": "bytes32"},
            {"indexed": False, "internalType": "string", "name": "issuerName", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "receiverName", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "courseName", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "department", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "issuedDate", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "expiryDate", "type": "uint256"}
        ],
        "name": "CertificateIssued",
        "type": "event"
    }
]

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Load the private key and create account
private_key = os.getenv('PRIVATE_KEY')
account = Account.from_key(private_key)


def get_nonce():
    return w3.eth.get_transaction_count(account.address)


@app.route('/issue_certificate', methods=['POST'])
def issue_certificate():
    data = request.json
    issuer_name = data.get('issuer_name')
    receiver_name = data.get('receiver_name')
    course_name = data.get('course_name')
    department = data.get('department')
    expiry_date = data.get('expiry_date')  # Expected in YYYY-MM-DD format

    if not all([issuer_name, receiver_name, course_name, department, expiry_date]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Convert expiry_date to Unix timestamp
        expiry_timestamp = int(datetime.strptime(expiry_date, "%Y-%m-%d").timestamp())

        # Build the transaction
        txn = contract.functions.issueCertificate(
            issuer_name, receiver_name, course_name, department, expiry_timestamp
        ).build_transaction({
            'from': account.address,
            'nonce': get_nonce(),
            'gas': 300000,  # Increased gas limit for the more complex function
            'gasPrice': w3.eth.gas_price,
        })

        # Sign and send the transaction
        signed_txn = account.sign_transaction(txn)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction to be mined
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Get the certificate ID from the event logs
        certificate_id = None
        for log in tx_receipt['logs']:
            try:
                decoded_log = contract.events.CertificateIssued().process_log(log)
                certificate_id = decoded_log['args']['certificateId'].hex()
                break
            except:
                continue

        if certificate_id is None:
            raise Exception("Failed to retrieve certificate ID from transaction logs")

        return jsonify({
            "message": "Certificate issued successfully",
            "certificate_id": certificate_id,
            "transaction_hash": tx_hash.hex()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/validate_certificate/<certificate_id>', methods=['GET'])
def validate_certificate(certificate_id):
    try:
        # Ensure the certificate_id is in bytes32 format
        certificate_id_bytes = bytes.fromhex(certificate_id.replace('0x', ''))

        # Call the smart contract function
        is_valid, cert_data = contract.functions.validateCertificate(certificate_id_bytes).call()

        # Convert Unix timestamps to readable date strings
        issued_date = datetime.utcfromtimestamp(cert_data[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
        expiry_date = datetime.utcfromtimestamp(cert_data[5]).strftime('%Y-%m-%d %H:%M:%S UTC')

        return jsonify({
            "certificate_id": certificate_id,
            "is_valid": is_valid,
            "certificate_info": {
                "issuer_name": cert_data[0],
                "receiver_name": cert_data[1],
                "course_name": cert_data[2],
                "department": cert_data[3],
                "issued_date": issued_date,
                "expiry_date": expiry_date,
                "is_active": cert_data[6]
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_balance', methods=['GET'])
def check_balance():
    try:
        balance = w3.eth.get_balance(account.address)
        return jsonify({
            "account": account.address,
            "balance_wei": balance,
            "balance_eth": w3.from_wei(balance, 'ether')
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/contract_address', methods=['GET'])
def get_contract_address():
    return jsonify({"contract_address": contract_address}), 200


@app.route('/account_address', methods=['GET'])
def get_account_address():
    return jsonify({"account_address": account.address}), 200

if __name__ == '__main__':
    app.run(debug=True)
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from eth_account import Account
from flask import Flask, request, jsonify
from flask import send_file
from flask_cors import CORS  # Import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from web3 import Web3
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}})
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
jwt = JWTManager(app)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_NODE_URL')))
w3.eth.default_chain_id = int(os.getenv('CHAIN_ID', '17000'))  # Holesky chain ID
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
contract = w3.eth.contract(address=contract_address, abi=contract_abi)
private_key = os.getenv('PRIVATE_KEY')
account = Account.from_key(private_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('lms.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_nonce():
    return w3.eth.get_transaction_count(account.address)

@app.route('/api/upload_document/<course_id>', methods=['POST'])
def upload_document(course_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        course_folder = os.path.join(app.config['UPLOAD_FOLDER'], course_id)
        os.makedirs(course_folder, exist_ok=True)
        file_path = os.path.join(course_folder, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/list_documents/<course_id>', methods=['GET'])
def list_documents(course_id):
    course_folder = os.path.join(app.config['UPLOAD_FOLDER'], course_id)
    if not os.path.exists(course_folder):
        return jsonify({'documents': []}), 200
    documents = [f for f in os.listdir(course_folder) if allowed_file(f)]
    return jsonify({'documents': documents}), 200

@app.route('/api/download_document/<course_id>/<filename>', methods=['GET'])
def download_document(course_id, filename):
    course_folder = os.path.join(app.config['UPLOAD_FOLDER'], course_id)
    file_path = os.path.join(course_folder, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and user['password'] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/courses', methods=['GET'])
# @jwt_required()
def get_courses():
    conn = get_db_connection()
    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return jsonify([dict(course) for course in courses])

@app.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    name = request.json.get('name', None)
    instructor_id = request.json.get('instructor_id', None)

    if not name or not instructor_id:
        return jsonify({"msg": "Missing data"}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO courses (name, instructor_id) VALUES (?, ?)', (name, instructor_id))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Course created successfully"}), 201

@app.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_details(course_id):
    conn = get_db_connection()
    course = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    conn.close()
    if course:
        return jsonify(dict(course))
    else:
        return jsonify({"msg": "Course not found"}), 404

@app.route('/courses/<int:course_id>/assignments', methods=['GET'])
# @jwt_required()
def get_course_assignments(course_id):
    conn = get_db_connection()
    assignments = conn.execute('SELECT * FROM assignments WHERE course_id = ?', (course_id,)).fetchall()
    conn.close()
    return jsonify([dict(assignment) for assignment in assignments])

@app.route('/assignments/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_details(assignment_id):
    conn = get_db_connection()
    assignment = conn.execute('SELECT * FROM assignments WHERE id = ?', (assignment_id,)).fetchone()
    conn.close()
    if assignment:
        return jsonify(dict(assignment))
    else:
        return jsonify({"msg": "Assignment not found"}), 404

@app.route('/submissions', methods=['POST'])
@jwt_required()
def submit_assignment():
    student_id = request.json.get('student_id', None)
    assignment_id = request.json.get('assignment_id', None)
    content = request.json.get('content', None)

    if not student_id or not assignment_id or not content:
        return jsonify({"msg": "Missing data"}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO submissions (student_id, assignment_id, content) VALUES (?, ?, ?)',
                 (student_id, assignment_id, content))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Submission successful"}), 201

@app.route('/grades', methods=['POST'])
@jwt_required()
def add_grade():
    submission_id = request.json.get('submission_id', None)
    grade = request.json.get('grade', None)

    if not submission_id or grade is None:
        return jsonify({"msg": "Missing data"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE submissions SET grade = ? WHERE id = ?', (grade, submission_id))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Grade added successfully"}), 200


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
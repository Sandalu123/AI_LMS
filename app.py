from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500", "supports_credentials": True}})
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
jwt = JWTManager(app)


def get_db_connection():
    conn = sqlite3.connect('lms.db')
    conn.row_factory = sqlite3.Row
    return conn


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
@jwt_required()
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


if __name__ == '__main__':
    app.run(debug=True)
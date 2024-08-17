import sqlite3
import random

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('lms.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    is_instructor BOOLEAN
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    instructor_id INTEGER,
    FOREIGN KEY (instructor_id) REFERENCES users (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
)
''')

# Sample data
courses = [
    "Algebra",
    "Geometry",
    "Calculus",
    "Physics",
    "Chemistry"
]

# Create 5 instructors
for i in range(1, 6):
    cursor.execute("INSERT INTO users (username, password, is_instructor) VALUES (?, ?, ?)",
                   (f"instructor{i}", f"password{i}", True))

# Create 20 students
for i in range(1, 21):
    cursor.execute("INSERT INTO users (username, password, is_instructor) VALUES (?, ?, ?)",
                   (f"student{i}", f"password{i}", False))

# Create 5 courses
for i, course in enumerate(courses, start=1):
    cursor.execute("INSERT INTO courses (name, instructor_id) VALUES (?, ?)",
                   (course, i))

# Enroll students in random courses
for student_id in range(6, 26):  # Student IDs start from 6
    num_courses = random.randint(1, 3)
    course_ids = random.sample(range(1, 6), num_courses)
    for course_id in course_ids:
        cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                       (student_id, course_id))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully with dummy data.")
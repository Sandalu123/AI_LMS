import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('lms.db')
cursor = conn.cursor()

# Sample course names
course_names = [
    "Introduction to Python",
    "Advanced Mathematics",
    "Web Development Fundamentals",
    "Data Structures and Algorithms",
    "Machine Learning Basics",
    "Database Management Systems",
    "Computer Networks",
    "Software Engineering Principles",
    "Artificial Intelligence",
    "Mobile App Development"
]

# Sample assignment titles
assignment_titles = [
    "Midterm Project",
    "Final Exam",
    "Weekly Quiz",
    "Group Presentation",
    "Research Paper",
    "Coding Challenge",
    "Lab Report",
    "Case Study Analysis",
    "Portfolio Project",
    "Peer Review Exercise"
]

# Generate dummy courses
for course_name in course_names:
    instructor_id = random.randint(1, 5)  # Assuming we have 5 instructors from previous data
    cursor.execute("INSERT INTO courses (name, instructor_id) VALUES (?, ?)", (course_name, instructor_id))

# Generate dummy assignments
for _ in range(30):  # Creating 30 assignments
    course_id = random.randint(1, len(course_names))
    title = random.choice(assignment_titles)
    description = f"This is a description for the assignment: {title}"
    due_date = (datetime.now() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO assignments (course_id, title, description, due_date) 
    VALUES (?, ?, ?, ?)
    """, (course_id, title, description, due_date))

# Generate dummy submissions
for _ in range(100):  # Creating 100 submissions
    student_id = random.randint(6, 25)  # Assuming student IDs start from 6 and we have 20 students
    assignment_id = random.randint(1, 30)  # We created 30 assignments
    content = f"This is a submission for assignment {assignment_id} by student {student_id}"
    grade = round(random.uniform(60, 100), 2)  # Random grade between 60 and 100

    cursor.execute("""
    INSERT INTO submissions (student_id, assignment_id, content, grade) 
    VALUES (?, ?, ?, ?)
    """, (student_id, assignment_id, content, grade))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Dummy data generated successfully!")
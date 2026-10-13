from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"

# 1. DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 2. CREATE DATABASE TABLE
def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            course TEXT NOT NULL,
            section TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_table()

# 3. HTML DESIGN & TEMPLATE
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Database Management System</title>
    <style>
        body { font-family: Arial, sans-serif; background: #e3f2fd; margin: 0; padding: 20px; }
        h1 { text-align: center; color: #1565c0; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
        form { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
        input { padding: 10px; border: 1px solid #aaa; border-radius: 5px; font-size: 14px; }
        button { grid-column: span 2; padding: 10px; background: #1565c0; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0d47a1; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #1565c0; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Student Database Management System</h1>
        
        <!-- Add Student Form -->
        <form action="/add" method="POST">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="number" name="age" placeholder="Age" required>
            <input type="text" name="course" placeholder="Course" required>
            <input type="text" name="section" placeholder="Section" required>
            <input type="text" name="mobile" placeholder="Mobile Number" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <button type="submit">Add Student</button>
        </form>

        <h2>Student Records</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>Course</th>
                <th>Section</th>
                <th>Mobile</th>
                <th>Email</th>
            </tr>
            {% for student in students %}
            <tr>
                <td>{{ student.student_id }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.age }}</td>
                <td>{{ student.course }}</td>
                <td>{{ student.section }}</td>
                <td>{{ student.mobile }}</td>
                <td>{{ student.email }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

# 4. ROUTES
@app.route('/')
def index():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template_string(HTML, students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    age = request.form.get('age')
    course = request.form.get('course')
    section = request.form.get('section')
    mobile = request.form.get('mobile')
    email = request.form.get('email')

    if name and age and course and section and mobile and email:
        conn = get_db()
        conn.execute(
            "INSERT INTO students (name, age, course, section, mobile, email) VALUES (?, ?, ?, ?, ?, ?)",
            (name, age, course, section, mobile, email)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

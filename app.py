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

# 3. HTML DESIGN & TEMPLATE WITH SEARCH
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Database Management System</title>
    <style>
        body { font-family: Arial, sans-serif; background: #e3f2fd; margin: 0; padding: 20px; }
        h1, h2 { text-align: center; color: #1565c0; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;}
        form { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
        input { padding: 10px; border: 1px solid #aaa; border-radius: 5px; font-size: 14px; }
        button { grid-column: span 2; padding: 10px; background: #1565c0; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0d47a1; }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        .search-box input { flex: 1; }
        .search-box button { width: auto; grid-column: auto; padding: 10px 20px; }
        .reset-btn { background: #757575; text-decoration: none; color: white; padding: 10px 20px; border-radius: 5px; text-align: center; display: inline-block; line-height: normal; }
        .reset-btn:hover { background: #616161; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #1565c0; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Student Database Management System</h1>
        
        <!-- Add Student Form -->
        <h3>Add New Student</h3>
        <form action="/add" method="POST">
            <input type="text" name="name" placeholder="Full Name" required>
            <input type="number" name="age" placeholder="Age" required>
            <input type="text" name="course" placeholder="Course" required>
            <input type="text" name="section" placeholder="Section" required>
            <input type="text" name="mobile" placeholder="Mobile Number" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <button type="submit">Add Student</button>
        </form>
    </div>

    <div class="container">
        <h2>Student Records</h2>

        <!-- Search Form -->
        <form action="/" method="GET" class="search-box">
            <input type="text" name="search" placeholder="Search by ID, Name, Age, Course, or Mobile..." value="{{ request.args.get('search', '') }}">
            <button type="submit">Search</button>
            <a href="/" class="reset-btn">Reset</a>
        </form>

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
            {% if students %}
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
            {% else %}
                <tr>
                    <td colspan="7" style="text-align: center; color: #777;">No student records found.</td>
                </tr>
            {% endif %}
        </table>
    </div>
</body>
</html>
"""

# 4. ROUTES
@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    conn = get_db()
    
    if search_query:
        # Search across student_id, name, age, course, or mobile using SQL LIKE
        query = """
            SELECT * FROM students 
            WHERE student_id LIKE ? 
               OR name LIKE ? 
               OR age LIKE ? 
               OR course LIKE ? 
               OR mobile LIKE ?
        """
        wildcard_query = f"%{search_query}%"
        students = conn.execute(query, (wildcard_query, wildcard_query, wildcard_query, wildcard_query, wildcard_query)).fetchall()
    else:
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

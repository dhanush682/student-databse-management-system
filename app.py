
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
        CREATE TABLE IF NOT EXISTS students(
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

# 3. HTML DESIGN

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Student Database Management System</title>
<style>
body {
    font-family: Arial;
    background: #e3f2fd;
    margin: 0;
    padding: 20px;
}
h1 {
    text-align: center;
    color: #1565c0;
}
.container {
    max-width: 1100px;
    margin: auto;
    background: white;
    padding: 20px;
    border-radius: 12px;
}
input {
    padding: 10px;
    margin: 5px;
    border: 1px solid #aaa;
    border-radius: 5px;
}
button {
    padding: 10px 15px;
    background: #1565c0;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}
th, td {
    padding: 10px;
    border: 1px solid #ddd;
    text-align: center;
}
th {
    background: #1565c0;
    color: white;
}
a {
    text-decoration: none;
    color: #1565c0;
}
.delete {
    color: red;
}
.message {
    color: green;
    text-align: center;
}
</style>
</head>
<body>
<div class="container">
<h1>Student Database Management System</h1>

<h2>{{ 'Update Student' if student else 'Add Student' }}</h2>

<form method="POST" action="{{ url_for('update', sid=student['student_id']) if student else url_for('add') }}">
<input name="name" placeholder="Student Name" required value="{{ student['name'] if student else '' }}">
<input name="age" type="number" min="1" max="99" placeholder="Age" required value="{{ student['age'] if student else '' }}">
<input name="course" placeholder="Course" required value="{{ student['course'] if student else '' }}">
<input name="section" placeholder="Section" required value="{{ student['section'] if student else '' }}">
<input name="mobile" placeholder="Mobile Number" pattern="[0-9]{10}" title="Enter 10 digits" required value="{{ student['mobile'] if student else '' }}">
<input name="email" type="email" placeholder="Email" required value="{{ student['email'] if student else '' }}">
<button type="submit">{{ 'Update Student' if student else 'Add Student' }}</button>
{% if student %}
<a href="{{ url_for('index') }}">Cancel</a>
{% endif %}
</form>

<h2>Search Students</h2>
<form method="GET" action="{{ url_for('index') }}">
<input name="search" placeholder="Search by name, ID or course" value="{{ search }}">
<button type="submit">Search</button>
<a href="{{ url_for('index') }}">Show All</a>
</form>

<h2>Student Records ({{ students|length }})</h2>
{% if message %}
<p class="message">{{ message }}</p>
{% endif %}

<table>
<tr>
<th>ID</th>
<th>Name</th>
<th>Age</th>
<th>Course</th>
<th>Section</th>
<th>Mobile</th>
<th>Email</th>
<th>Actions</th>
</tr>
{% for s in students %}
<tr>
<td>{{ s['student_id'] }}</td>
<td>{{ s['name'] }}</td>
<td>{{ s['age'] }}</td>
<td>{{ s['course'] }}</td>
<td>{{ s['section'] }}</td>
<td>{{ s['mobile'] }}</td>
<td>{{ s['email'] }}</td>
<td>
<a href="{{ url_for('edit', sid=s['student_id']) }}">Edit</a> |
<a class="delete" href="{{ url_for('delete', sid=s['student_id']) }}" onclick="return confirm('Delete this student?')">Delete</a>
</td>
</tr>
{% else %}
<tr><td colspan="8">No student records found.</td></tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""

# 4. DISPLAY AND SEARCH STUDENTS

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    message = request.args.get("message", "")
    conn = get_db()

    if search:
        if search.isdigit():
            students = conn.execute("""
                SELECT * FROM students
                WHERE name LIKE ? OR course LIKE ? OR student_id = ?
                ORDER BY student_id
            """, ('%' + search + '%', '%' + search + '%', int(search))).fetchall()
        else:
            students = conn.execute("""
                SELECT * FROM students
                WHERE name LIKE ? OR course LIKE ? OR section LIKE ?
                ORDER BY student_id
            """, ('%' + search + '%', '%' + search + '%', '%' + search + '%')).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM students ORDER BY student_id"
        ).fetchall()

    conn.close()
    return render_template_string(
        HTML,
        students=students,
        student=None,
        search=search,
        message=message
    )

# 5. ADD STUDENT

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    course = request.form.get("course", "").strip()
    section = request.form.get("section", "").strip()
    mobile = request.form.get("mobile", "").strip()
    email = request.form.get("email", "").strip()

    if not all([name, age, course, section, mobile, email]):
        return "All fields are required.", 400

    try:
        age_value = int(age)
        if age_value < 1 or age_value > 99:
            return "Age must be between 1 and 99.", 400

        if len(mobile) != 10 or not mobile.isdigit():
            return "Mobile number must contain 10 digits.", 400

        conn = get_db()
        conn.execute("""
            INSERT INTO students(name, age, course, section, mobile, email)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (name, age_value, course, section, mobile, email))
        conn.commit()
        conn.close()
        return redirect(url_for("index", message="Student added successfully!"))
    except ValueError:
        return "Please enter a valid age.", 400
    except sqlite3.Error:
        return "Database error while adding student.", 500

# 6. OPEN EDIT FORM

@app.route("/edit/<int:sid>")
def edit(sid):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?", (sid,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found.", 404

    students = conn.execute(
        "SELECT * FROM students ORDER BY student_id"
    ).fetchall()
    conn.close()

    return render_template_string(
        HTML,
        students=students,
        student=student,
        search="",
        message=""
    )

# 7. UPDATE STUDENT

@app.route("/update/<int:sid>", methods=["POST"])
def update(sid):
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    course = request.form.get("course", "").strip()
    section = request.form.get("section", "").strip()
    mobile = request.form.get("mobile", "").strip()
    email = request.form.get("email", "").strip()

    if not all([name, age, course, section, mobile, email]):
        return "All fields are required.", 400

    try:
        age_value = int(age)
        if age_value < 1 or age_value > 99:
            return "Age must be between 1 and 99.", 400

        if len(mobile) != 10 or not mobile.isdigit():
            return "Mobile number must contain 10 digits.", 400

        conn = get_db()
        result = conn.execute("""
            UPDATE students
            SET name=?, age=?, course=?, section=?, mobile=?, email=?
            WHERE student_id=?
        """, (name, age_value, course, section, mobile, email, sid))

        conn.commit()
        conn.close()

        if result.rowcount == 0:
            return "Student not found.", 404

        return redirect(url_for("index", message="Student updated successfully!"))
    except ValueError:
        return "Please enter a valid age.", 400
    except sqlite3.Error:
        return "Database error while updating student.", 500

# 8. DELETE STUDENT

@app.route("/delete/<int:sid>")
def delete(sid):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE student_id = ?", (sid,))
    conn.commit()
    conn.close()
    return redirect(url_for("index", message="Student deleted successfully!"))

# 9. START APPLICATION

if __name__ == "__main__":
    create_table()
    app.run(debug=True)

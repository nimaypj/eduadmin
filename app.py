# =========================================
# IMPORTS
# =========================================

from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    flash, jsonify
)
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
import os


# =========================================
# APPLICATION CONFIGURATION
# =========================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["crud_db"]

students_collection = db["students"]
users_collection = db["users"]


# =========================================
# AUTHENTICATION DECORATORS
# =========================================

def login_required(f):
    """Ensure user is logged in before accessing route."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    """Ensure user has required role."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != role:
            return "Access Denied", 403
        return f(*args, **kwargs)
    return wrapper


# =========================================
# WEB ROUTES
# =========================================

@app.route("/")
@login_required
def index():
    """Display paginated list of students."""
    page = request.args.get("page", 1, type=int)
    per_page = 5

    students = list(
        students_collection.find()
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    for student in students:
        student["_id"] = str(student["_id"])

    return render_template(
        "index.html",
        students=students,
        page=page
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["role"] = user.get("role", "viewer")
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Logout current user."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/add", methods=["GET", "POST"])
@login_required
@role_required("admin")
def add_student():
    """Add a new student (Admin only)."""
    if request.method == "POST":
        student_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "course": request.form.get("course")
        }
        students_collection.insert_one(student_data)
        return redirect(url_for("index"))

    return render_template("add.html")


# =========================================
# REST API ROUTES
# =========================================

@app.route("/api/students", methods=["GET"])
@login_required
def api_get_students():
    """Return all students as JSON."""
    students = list(students_collection.find())

    for student in students:
        student["_id"] = str(student["_id"])

    return jsonify(students)


@app.route("/api/students", methods=["POST"])
@login_required
@role_required("admin")
def api_add_student():
    """Create new student via API."""
    data = request.get_json()

    new_student = {
        "name": data["name"],
        "age": data["age"],
        "course": data["course"]
    }

    result = students_collection.insert_one(new_student)
    new_student["_id"] = str(result.inserted_id)

    return jsonify(new_student), 201


@app.route("/api/students/<id>", methods=["PUT"])
@login_required
@role_required("admin")
def api_update_student(id):
    """Update student via API."""
    data = request.get_json()

    students_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )

    return jsonify({"message": "Student updated"})


@app.route("/api/students/<id>", methods=["DELETE"])
@login_required
@role_required("admin")
def api_delete_student(id):
    """Delete student via API."""
    students_collection.delete_one({"_id": ObjectId(id)})

    return jsonify({"message": "Student deleted"})


# =========================================
# APPLICATION ENTRY POINT
# =========================================

if __name__ == "__main__":
    app.run(debug=True)

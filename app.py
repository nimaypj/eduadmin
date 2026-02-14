from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from flask import jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
client = MongoClient(os.environ.get("MONGO_URI"))

db = client["crud_db"]
students_collection = db["students"]
users_collection = db["users"]


# ===============================
# CREATE DEFAULT USERS IF MISSING
# ===============================
# ===============================
# ENSURE USERS HAVE ROLES
# ===============================

admin_user = users_collection.find_one({"username": "admin"})
if not admin_user:
    users_collection.insert_one({
        "username": "admin",
        "password": generate_password_hash("admin123"),
        "role": "admin"
    })
elif "role" not in admin_user:
    users_collection.update_one(
        {"username": "admin"},
        {"$set": {"role": "admin"}}
    )

viewer_user = users_collection.find_one({"username": "viewer"})
if not viewer_user:
    users_collection.insert_one({
        "username": "viewer",
        "password": generate_password_hash("viewer123"),
        "role": "viewer"
    })
elif "role" not in viewer_user:
    users_collection.update_one(
        {"username": "viewer"},
        {"$set": {"role": "viewer"}}
    )


# ===============================
# LOGIN REQUIRED DECORATOR
# ===============================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ===============================
# ROLE REQUIRED DECORATOR
# ===============================
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("role") != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ===============================
# LOGIN ROUTE
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["role"] = user["role"]
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# ===============================
# HOME (Protected)
# ===============================
@app.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5   # number of records per page

    query = request.args.get("search")

    if query:
        filter_query = {
            "name": {"$regex": query, "$options": "i"}
        }
    else:
        filter_query = {}

    total_students = students_collection.count_documents(filter_query)

    students = list(
        students_collection.find(filter_query)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    total_pages = (total_students + per_page - 1) // per_page

    return render_template(
        "index.html",
        students=students,
        total=total_students,
        page=page,
        total_pages=total_pages,
        role=session.get("role"),
        search=query
    )



# ===============================
# ADD (Admin Only)
# ===============================
@app.route("/add", methods=["GET", "POST"])
@login_required
@role_required("admin")
def add_student():
    if request.method == "POST":
        students_collection.insert_one({
            "name": request.form["name"],
            "age": request.form["age"],
            "course": request.form["course"]
        })

        flash("Student added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


# ===============================
# EDIT (Admin Only)
# ===============================
@app.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_student(id):
    student = students_collection.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        students_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": request.form["name"],
                "age": request.form["age"],
                "course": request.form["course"]
            }}
        )

        flash("Student updated successfully!", "info")
        return redirect(url_for("index"))

    return render_template("edit.html", student=student)


# ===============================
# DELETE (Admin Only)
# ===============================
@app.route("/delete/<id>")
@login_required
@role_required("admin")
def delete_student(id):
    students_collection.delete_one({"_id": ObjectId(id)})
    flash("Student deleted successfully!", "danger")
    return redirect(url_for("index"))


# ===============================
# 403 ERROR HANDLER
# ===============================
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
# ===============================
# REST API ENDPOINTS
# ===============================

@app.route("/api/students", methods=["GET"])
@login_required
def api_get_students():
    students = list(students_collection.find())

    for student in students:
        student["_id"] = str(student["_id"])

    return jsonify(students)


@app.route("/api/students", methods=["POST"])
@login_required
@role_required("admin")
def api_add_student():
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
    data = request.get_json()

    students_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "name": data["name"],
            "age": data["age"],
            "course": data["course"]
        }}
    )

    return jsonify({"message": "Student updated"})


@app.route("/api/students/<id>", methods=["DELETE"])
@login_required
@role_required("admin")
def api_delete_student(id):
    students_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Student deleted"})

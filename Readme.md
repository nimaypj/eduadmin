📘 EduAdmin — Role-Based Student Management System
🚀 Live Demo

https://eduadmin.onrender.com

📌 Overview

EduAdmin is a production-ready role-based student management system built using Flask and MongoDB Atlas.
It implements authentication, authorization, RESTful APIs, and cloud deployment.

✨ Features

🔐 Session-based authentication

👥 Role-based access control (Admin / Viewer)

📄 Server-side pagination

🔎 Search functionality

🌐 REST API endpoints

☁️ Deployed on Render

🗄 MongoDB Atlas cloud database

⚙️ Environment variable configuration

🚀 Gunicorn production server

🛠 Tech Stack

Python 3

Flask

MongoDB Atlas

PyMongo

Gunicorn

Render (Deployment)

📡 REST API Endpoints
| Method | Endpoint           | Description                 |
| ------ | ------------------ | --------------------------- |
| GET    | /api/students      | Fetch all students          |
| POST   | /api/students      | Create student (Admin only) |
| PUT    | /api/students/<id> | Update student (Admin only) |
| DELETE | /api/students/<id> | Delete student (Admin only) |


Session-based login system

Secure password hashing using Werkzeug

Role enforcement via custom decorators

API routes protected using authentication checks

🧠 Architecture Flow

Client → HTTP Request → Flask Routes → MongoDB → JSON/HTML Response

⚙️ Run Locally
git clone https://github.com/YOUR_USERNAME/eduadmin.git
cd eduadmin
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py


Create a .env or set environment variables:

SECRET_KEY=your_secret
MONGO_URI=your_mongo_connection_string

📦 Deployment

Hosted on Render

Uses Gunicorn as WSGI server

MongoDB Atlas for database

Environment variables for secure configuration

📈 Future Improvements

JWT-based API authentication

API documentation with Swagger

Rate limiting

Blueprint-based architecture

React frontend integration

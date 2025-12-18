from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
import os
import google.generativeai as genai

# ---------------- CONFIG ---------------- #
app = Flask(__name__)
app.secret_key = "change-this-secret"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Demo users
users = {"demo": "password123"}

# ---------------- AUTH ---------------- #
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in users and users[u] == p:
            session["username"] = u
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# ---------------- MAIN ---------------- #
@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session["username"])


@app.route("/get_response", methods=["POST"])
@login_required
def get_response():
    history = request.json["history"]
    username = session["username"]

    prompt = f"""
You are Nyay AI, an expert assistant on Indian Law.
Respond clearly and professionally.
User name: {username}

"""

    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"

    response = model.generate_content(prompt)

    return jsonify({
        "response": response.text
    })


if __name__ == "__main__":
    app.run()

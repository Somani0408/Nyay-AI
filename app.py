from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
import google.generativeai as genai
import os


# ---------------- CONFIG ---------------- #
app = Flask(__name__)
app.secret_key = "change-this-secret"

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
    try:
        history = request.json.get("history", [])
        username = session.get("username", "User")

        # ✅ Get API key at runtime
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"response": "Server configuration error."}), 500

        # ✅ Initialize Gemini INSIDE the function
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
You are Nyay AI, an expert assistant on Indian Law.
Answer clearly and professionally.
User name: {username}

"""

        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"

        result = model.generate_content(prompt)

        if not result or not getattr(result, "text", None):
            return jsonify({
                "response": "I couldn't generate a response. Please rephrase your question."
            })

        return jsonify({"response": result.text})

    except Exception as e:
        print("🔥 GEMINI ERROR:", e)
        return jsonify({
            "response": "Temporary server error. Please try again."
        }), 500

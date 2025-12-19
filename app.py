from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
from google import genai
import os

# ---------------- GEMINI CLIENT ---------------- #
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ---------------- APP CONFIG ---------------- #
app = Flask(__name__)
app.secret_key = "change-this-secret"

users = {"demo": "password123"}

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
        u = request.form.get("username")
        p = request.form.get("password")
        if u in users and users[u] == p:
            session["username"] = u
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session["username"])

@app.route("/get_response", methods=["POST"])
@login_required
def get_response():
    try:
        data = request.get_json()
        history = data.get("history", [])
        username = session.get("username", "User")

        prompt = f"You are Nyay AI, an expert assistant on Indian Law.\nUser name: {username}\n"

        for msg in history:
            prompt += f"{msg['role']}: {msg['content']}\n"

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        return jsonify({"response": response.text})

    except Exception as e:
        print("🔥 GEMINI ERROR:", e)
        return jsonify({"response": "Temporary server error"}), 500

if __name__ == "__main__":
    app.run()

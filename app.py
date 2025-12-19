from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
from groq import Groq
import os

# ---------------- GROQ CONFIG ---------------- #
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---------------- APP CONFIG ---------------- #
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


# ---------------- MAIN ---------------- #
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

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Nyay AI, an expert assistant on Indian Law. "
                    "Answer clearly, professionally, and accurately."
                )
            }
        ]

        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        reply = completion.choices[0].message.content
        return jsonify({"response": reply})

    except Exception as e:
        print("🔥 GROQ ERROR:", e)
        return jsonify({
            "response": "Temporary server error. Please try again."
        }), 500


if __name__ == "__main__":
    app.run()

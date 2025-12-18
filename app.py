from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from llama_cpp import Llama
import os
from functools import wraps

# 1. Initialize Flask App
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Simple user database (demo only)
users = {
    'demo': 'password123'
}

# 2. Define the path to your GGUF model file
model_filename = "./indian-legal-model/outpt_file.gguf"
model_path = os.path.abspath(model_filename)
print(f"Loading GGUF model from: {model_path}")

# 3. Load the Model
try:
    llm = Llama(
        model_path=model_path,
        n_gpu_layers=0,   # IMPORTANT: CPU only
        n_ctx=4096,
        verbose=True,
    )
    print("GGUF Model loaded successfully!")
except Exception as e:
    print("ERROR: Failed to load GGUF model.")
    print(e)
    exit()

# ---------------- AUTH ---------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if username in users:
            return render_template('signup.html', error='Username already exists')

        if password != confirm:
            return render_template('signup.html', error='Passwords do not match')

        users[username] = password
        session['username'] = username
        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ---------------- MAIN APP ---------------- #

@app.route("/")
@login_required
def index():
    username = session.get('username', 'User')
    return render_template("index.html", username=username)


@app.route("/get_response", methods=["POST"])
@login_required
def get_response():
    try:
        history = request.json["history"]
        username = session.get('username', 'User')

        prompt = f"""### Instruction:
You are Nyay AI, an esteemed legal scholar and expert assistant on Indian Law.
Maintain a formal and professional tone.
The user's name is {username}. Address them naturally.

"""

        for msg in history:
            if msg["role"] == "user":
                prompt += f"### User:\n{msg['content']}\n\n"
            else:
                prompt += f"### Assistant:\n{msg['content']}\n\n"

        prompt += "### Assistant:\n"

        output = llm(
            prompt,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["### User:", "### Instruction:"],
        )

        response = output["choices"][0]["text"].strip()
        return jsonify({"response": response})

    except Exception as e:
        print("Inference error:", e)
        return jsonify({"response": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)

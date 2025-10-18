from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = "cambia_questa_chiave"

PARTECIPANTI = [
    "Abramo", "Edoardo", "Alex", "Bianchi", "Vittorio",
    "Riccardo", "Diego", "Giosuè", "Lauber", "Gottardo",
    "Lovato", "Mosconi", "Roman"
]

ADMIN_PASSWORDS = {
    "Abramo": "abramo208",
    "Edoardo": "edoardo104"
}

DATA_FILE = "data.json"

# inizializza dati se non esistono
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({p: {"punti":0} for p in PARTECIPANTI}, f, ensure_ascii=False, indent=2)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()

        # controllo admin
        if username in ADMIN_PASSWORDS and password == ADMIN_PASSWORDS[username]:
            session["user"] = username
            session["is_admin"] = True
            return redirect(url_for("admin_page"))

        # controllo viewer
        if username in PARTECIPANTI:
            session["user"] = username
            session["is_admin"] = False
            return redirect(url_for("viewer_page"))

        error = "Nome o password non validi"

    return render_template("login.html", error=error)

@app.route("/admin", methods=["GET","POST"])
def admin_page():
    if "user" not in session or not session.get("is_admin", False):
        return redirect(url_for("login"))

    data = load_data()
    if request.method == "POST":
        partecipante = request.form.get("partecipante")
        punti = int(request.form.get("punti","0"))
        if partecipante in data:
            data[partecipante]["punti"] += punti
            save_data(data)
        return redirect(url_for("admin_page"))

    return render_template("admin.html", user=session["user"], data=data)

@app.route("/viewer")
def viewer_page():
    if "user" not in session:
        return redirect(url_for("login"))

    data = load_data()
    return render_template("viewer.html", user=session["user"], data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

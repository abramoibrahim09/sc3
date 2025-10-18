from flask import Flask, render_template, request, redirect, url_for, session
import os, json

app = Flask(__name__)
app.secret_key = "cambia_questa_chiave_con_qualcosa_di_sicuro"

PARTECIPANTI = [
    "Abramo", "Edoardo", "Alex", "Bianchi", "Vittorio",
    "Riccardo", "Diego", "Giosuè", "Lauber", "Gottardo",
    "Lovato", "Mosconi", "Roman"
]

# password admin
ADMIN_PASSWORDS = {
    "abramo": "abramo208",
    "edoardo": "edoardo104",
    "edo": "edoardo104"
}

DATA_FILE = "data.json"

def ensure_data():
    if not os.path.exists(DATA_FILE):
        data = {p: {"punti": 0} for p in PARTECIPANTI}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    ensure_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

ensure_data()

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username_input = (request.form.get("username") or "").strip()
        password_input = (request.form.get("password") or "").strip()
        username_lower = username_input.lower()

        # DEBUG: stampa chi prova a fare login
        print(f"[DEBUG] Login attempt: {username_input}, password: {password_input}")

        # controllo admin
        if username_lower in ADMIN_PASSWORDS and password_input == ADMIN_PASSWORDS[username_lower]:
            canonical = "Edoardo" if username_lower.startswith("edo") else "Abramo"
            session["user"] = canonical
            session["is_admin"] = True
            print(f"[DEBUG] Admin login riuscito: {canonical}")
            return redirect(url_for("admin_page"))

        # controllo partecipante viewer
        for p in PARTECIPANTI:
            if username_lower == p.lower():
                session["user"] = p
                session["is_admin"] = False
                print(f"[DEBUG] Viewer login: {p}")
                return redirect(url_for("viewer_page"))

        error = "Nome o password non validi"
        print(f"[DEBUG] Login fallito per: {username_input}")

    return render_template("login.html", error=error)

@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    if "user" not in session or not session.get("is_admin"):
        return redirect(url_for("login"))

    data = load_data()

    if request.method == "POST":
        partecipante = request.form.get("partecipante")
        punti_raw = request.form.get("punti", "0")
        try:
            punti = int(punti_raw)
        except:
            punti = 0
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
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, send_file
import csv
import os

app = Flask(__name__)
app.secret_key = "tuo_secret_key_sicuro"

# Lista partecipanti
PARTECIPANTI = [
    "Abramo", "Edoardo", "Alex", "Bianchi", "Vittorio",
    "Riccardo", "Diego", "Giosuè", "Lauber", "Gottardo",
    "Lovato", "Mosconi", "Roman"
]

# Admin e password
ADMINS = {
    "Abramo": "abramo208",
    "Edoardo": "edoardo104"
}

# File dati (opzionale, per persistenza)
DATA_FILE = "data.csv"

# Categorie punti
CATEGORIE = {
    "INTERROGATO": 3,
    "ORDINE INTERROGATI": 4,
    "VOTO": 5,
    "RITARDO PROF (>6 min)": 2,
    "MIGLIORE CLASSE": 3,
    "PEGGIORE CLASSE": -3,
    "ANNOTAZIONE": 1,
    "NOTA DISCIPLINARE": -4,
    "RITARDO ALUNNO (>5 min)": 2,
    "INIZIO INTERROGAZIONI": 2
}

# Inizializza dati
if os.path.exists(DATA_FILE):
    data = {}
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["partecipante"]] = {"punti": int(row["punti"])}
else:
    data = {p: {"punti": 0} for p in PARTECIPANTI}

# ---- LOGIN ----
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_input = request.form.get("username", "").strip()
        password_input = request.form.get("password", "").strip()

        # Controllo admin (case-insensitive)
        for admin_name, admin_pass in ADMINS.items():
            if username_input.lower() == admin_name.lower() and password_input == admin_pass:
                session["user"] = admin_name
                session["admin"] = True
                return redirect(url_for("admin_page"))

        # Controllo visualizzatori
        for p in PARTECIPANTI:
            if username_input.lower() == p.lower():
                session["user"] = p
                session["admin"] = False
                return redirect(url_for("viewer_page"))

        error = "Nome utente o password non validi!"
        return render_template("login.html", error=error)

    return render_template("login.html")

# ---- ADMIN ----
@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    if "user" not in session or not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        partecipante = request.form.get("partecipante")
        punti = int(request.form.get("punti", 0))
        categoria = request.form.get("categoria")
        if partecipante in data:
            data[partecipante]["punti"] += punti
            save_data()
        return redirect(url_for("admin_page"))

    return render_template("admin.html", user=session["user"], data=data, categorie=CATEGORIE)

# ---- VIEWER ----
@app.route("/viewer")
def viewer_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("viewer.html", data=data)

# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---- CSV ----
@app.route("/export_csv")
def export_csv():
    filename = "classifica.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Partecipante", "Punti"])
        for p, info in data.items():
            writer.writerow([p, info["punti"]])
    return send_file(filename, as_attachment=True)

# ---- SALVATAGGIO DATI ----
def save_data():
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["partecipante", "punti"])
        for p, info in data.items():
            writer.writerow([p, info["punti"]])

if __name__ == "__main__":
    app.run(debug=True)

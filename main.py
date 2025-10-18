from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import csv

app = Flask(__name__)
app.secret_key = "supersegreto123"  # Cambia con qualcosa di sicuro

# File dove salvare dati
DATA_FILE = "data.json"

# Admin e password
ADMINS = {"Abramo": "abramo208", "Edoardo": "edoardo104"}

# Partecipanti totali
PARTECIPANTI = [
    "Abramo","Edoardo","Alex","Bianchi","Vittorio",
    "Riccardo","Diego","Giosuè","Lauber","Gottardo",
    "Lovato","Mosconi","Roman"
]

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

# Inizializza file dati
if not os.path.exists(DATA_FILE):
    data = {p: {"punti": 0} for p in PARTECIPANTI}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# Funzione per salvare dati
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password", "")
        if username in ADMINS and ADMINS[username] == password:
            session["user"] = username
            session["admin"] = True
            return redirect(url_for("admin_page"))
        elif username in PARTECIPANTI:
            session["user"] = username
            session["admin"] = False
            return redirect(url_for("viewer_page"))
        else:
            error = "Nome utente o password non validi!"
            return render_template("login.html", error=error)
    return render_template("login.html")

# Admin page
@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    if "user" not in session or not session.get("admin"):
        return redirect(url_for("login"))
    return render_template("admin.html", user=session["user"], data=data, categorie=CATEGORIE)

# Visualizzatore page
@app.route("/viewer")
def viewer_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("viewer.html", data=data)

# Aggiornamento punti
@app.route("/update_points", methods=["POST"])
def update_points():
    if "user" not in session or not session.get("admin"):
        return redirect(url_for("login"))
    partecipante = request.form.get("partecipante")
    categoria = request.form.get("categoria")
    punti = request.form.get("punti")
    if partecipante in data:
        try:
            punti = int(punti)
        except:
            punti = 0
        data[partecipante]["punti"] += punti
        save_data()
    return redirect(url_for("admin_page"))

# Esporta CSV
@app.route("/export_csv")
def export_csv():
    if "user" not in session or not session.get("admin"):
        return redirect(url_for("login"))
    csv_file = "classifica.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Partecipante", "Punti"])
        for p, d in data.items():
            writer.writerow([p, d["punti"]])
    return f"CSV esportato correttamente in {csv_file}"

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

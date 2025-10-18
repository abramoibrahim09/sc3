from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os, json, csv

app = Flask(__name__)
app.secret_key = "cambia_questa_chiave_con_qualcosa_di_sicuro"

# partecipanti (nomi ufficiali visualizzati)
PARTECIPANTI = [
    "Abramo", "Edoardo", "Alex", "Bianchi", "Vittorio",
    "Riccardo", "Diego", "Giosuè", "Lauber", "Gottardo",
    "Lovato", "Mosconi", "Roman"
]

# password admin: gli utenti possono inserire "Abramo" o "abramo" o "ABRAMO" — matching case-insensitive
# accetto anche 'edo' o 'edoardo' come input per Edoardo
ADMIN_PASSWORDS = {
    "abramo": "abramo208",
    "edoardo": "edoardo104",
    "edo": "edoardo104"
}

# categorie punti
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

DATA_FILE = "data.json"

# inizializza dati persistenti in JSON
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

# ---------- ROUTE ----------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_input = (request.form.get("username") or "").strip()
        password_input = (request.form.get("password") or "").strip()

        if not username_input:
            return render_template("login.html", error="Inserisci il nome")

        username_l = username_input.lower()

        # controllo admin case-insensitive (accetta 'edo' o 'edoardo')
        if username_l in ADMIN_PASSWORDS and password_input == ADMIN_PASSWORDS[username_l]:
            # normalizza il nome per sessione: usa la forma canonica (prima lettera maiuscola)
            canonical = "Edoardo" if username_l.startswith("edo") else "Abramo"
            session["user"] = canonical
            session["is_admin"] = True
            return redirect(url_for("admin_page"))

        # controllo partecipante (case-insensitive)
        for p in PARTECIPANTI:
            if username_l == p.lower():
                session["user"] = p
                session["is_admin"] = False
                return redirect(url_for("viewer_page"))

        return render_template("login.html", error="Nome o password non validi")
    return render_template("login.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    if "user" not in session or not session.get("is_admin"):
        return redirect(url_for("login"))

    data = load_data()

    # POST semplice per aggiornare punti (form action post verso questa route)
    if request.method == "POST":
        partecipante = request.form.get("partecipante")
        punti_raw = request.form.get("punti", "0")
        categoria = request.form.get("categoria", "MANUALE")
        try:
            punti = int(punti_raw)
        except:
            punti = 0
        if partecipante in data:
            data[partecipante]["punti"] += punti
            # salva
            save_data(data)
        return redirect(url_for("admin_page"))

    return render_template("admin.html", user=session.get("user"), data=data, categorie=CATEGORIE)

@app.route("/viewer")
def viewer_page():
    if "user" not in session:
        return redirect(url_for("login"))
    data = load_data()
    return render_template("viewer.html", data=data, user=session.get("user"))

@app.route("/export_csv")
def export_csv():
    if "user" not in session or not session.get("is_admin"):
        return redirect(url_for("login"))
    data = load_data()
    filename = "classifica.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Partecipante", "Punti"])
        for p, d in data.items():
            writer.writerow([p, d.get("punti", 0)])
    return send_file(filename, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# fallback sicuro
@app.errorhandler(500)
def internal(e):
    return "Errore interno server", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

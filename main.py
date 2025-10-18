from flask import Flask, render_template, request, redirect, url_for, session

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

# Mock dati classifica
data = {p: {"punti": 0} for p in PARTECIPANTI}

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

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password", "")

        # Controllo admin
        if username in ADMINS and ADMINS[username] == password:
            session["user"] = username
            session["admin"] = True
            return redirect(url_for("admin_page"))

        # Controllo visualizzatore
        if username in PARTECIPANTI:
            session["user"] = username
            session["admin"] = False
            return redirect(url_for("viewer_page"))

        error = "Nome utente o password non validi!"
        return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    if "user" not in session or not session.get("admin"):
        return redirect(url_for("login"))
    return render_template("admin.html", user=session["user"], data=data, categorie=CATEGORIE)


@app.route("/viewer")
def viewer_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("viewer.html", data=data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

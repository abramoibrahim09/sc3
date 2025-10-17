from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# File dati
DATA_FILE = 'class_data.json'

# Partecipanti
partecipanti = [
    "Abramo", "Edoardo", "Alex", "Bianchi", "Vittorio", "Riccardo",
    "Diego", "Giosuè", "Lauber", "Gottardo", "Lovato", "Mosconi", "Roman"
]

# Admin
admins = ["Abramo", "Edoardo"]

# Categorie punti
categorie = {
    "INTERROGATO": 3,
    "ORDINE_INTERROGATI": 4,
    "VOTO": 5,
    "RITARDO_PROF": 2,
    "MIGLIORE_CLASSE": 3,
    "PEGGIORE_CLASSE": 3,
    "ANNOTAZIONE": 1,
    "NOTA_DISCIPLINARE": 4,
    "RITARDO_ALUNNO": 2,
    "INIZIO_INTERROGAZIONI": 2
}

# Inizializza dati se non esiste
if not os.path.exists(DATA_FILE):
    data = {p: {'punti': 0, 'storico': []} for p in partecipanti}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Funzioni utili
def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Pagina login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username in partecipanti:
            if username in admins:
                return redirect(url_for('admin', user=username))
            else:
                return redirect(url_for('viewer', user=username))
        else:
            return "Nome non valido"
    return render_template('login.html')

# Pagina admin
@app.route('/admin/<user>')
def admin(user):
    data = load_data()
    return render_template('admin.html', data=data, user=user, categorie=categorie.keys())

# Pagina viewer
@app.route('/viewer/<user>')
def viewer(user):
    data = load_data()
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['punti'], reverse=True))
    return render_template('viewer.html', data=sorted_data, user=user)

# Aggiorna punti (ajax)
@app.route('/update_points', methods=['POST'])
def update_points():
    data = load_data()
    partecipante = request.form['partecipante']
    categoria = request.form['categoria']
    punti = int(request.form['punti'])
    note = request.form.get('note', '')
    if partecipante in data:
        data[partecipante]['punti'] += punti
        data[partecipante]['storico'].append({'categoria': categoria, 'punti': punti, 'note': note})
        save_data(data)
        return jsonify({'status': 'success', 'punti': data[partecipante]['punti']})
    return jsonify({'status': 'error'})

# Esporta CSV
@app.route('/export_csv')
def export_csv():
    import csv
    data = load_data()
    with open('classifica.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Partecipante', 'Punti'])
        for p, d in data.items():
            writer.writerow([p, d['punti']])
    return "CSV esportato come classifica.csv"

if __name__ == '__main__':
    app.run(debug=True)
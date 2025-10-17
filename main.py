from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

DATA_FILE = 'class_data.json'
USERS_FILE = 'users.json'

PARTECIPANTI = [
    "Abramo", "Edoardo", "Alex", "Bianchi", "Vittorio", "Riccardo",
    "Diego", "Giosuè", "Lauber", "Gottardo", "Lovato", "Mosconi", "Roman"
]

CATEGORIE = {
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

ADMIN_CREDENTIALS_PLAINTEXT = {
    "Abramo": "abramo208",
    "Edoardo": "edoardo104"
}

# Creazione file utenti e hash password
def init_users_file():
    if not os.path.exists(USERS_FILE):
        users = {}
        for p in PARTECIPANTI:
            users[p] = {"role": "viewer", "password_hash": None}
        for a, pwd in ADMIN_CREDENTIALS_PLAINTEXT.items():
            users[a]["role"] = "admin"
            users[a]["password_hash"] = generate_password_hash(pwd)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        logging.info('Created users.json with admin hashes')

def init_data_file():
    if not os.path.exists(DATA_FILE):
        data = {p: {'punti': 0, 'storico': []} for p in PARTECIPANTI}
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
        logging.info('Created class_data.json with initial participants')

def load_data():
    init_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def load_users():
    init_users_file()
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

init_users_file()
init_data_file()

@app.route('/', methods=['GET', 'POST', 'HEAD'])
@app.route('/login', methods=['GET', 'POST', 'HEAD'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username:
                return render_template('login.html', error='Inserisci un nome')

            users = load_users()
            if username not in users:
                return render_template('login.html', error='Nome non valido')

            role = users[username].get('role', 'viewer')

            if role == 'admin':
                pwd_hash = users[username].get('password_hash')
                if not pwd_hash:
                    return render_template('login.html', error='Admin privo di password, contatta responsabile')
                if not password or not check_password_hash(pwd_hash, password):
                    return render_template('login.html', error='Password errata')
                return redirect(url_for('admin', user=username))
            else:
                return redirect(url_for('viewer', user=username))
        return render_template('login.html')
    except Exception as e:
        logging.exception('Errore nella route /login')
        return f"Errore interno: {e}", 500

@app.route('/admin/<user>', methods=['GET'])
def admin(user):
    try:
        users = load_users()
        if user not in users or users[user].get('role') != 'admin':
            return "Accesso negato", 403
        data = load_data()
        return render_template('admin.html', data=data, user=user, categorie=CATEGORIE)
    except Exception as e:
        logging.exception('Errore /admin')
        return f"Errore interno: {e}", 500

@app.route('/viewer/<user>')
def viewer(user):
    try:
        data = load_data()
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['punti'], reverse=True))
        return render_template('viewer.html', data=sorted_data, user=user)
    except Exception as e:
        logging.exception('Errore /viewer')
        return f"Errore interno: {e}", 500

@app.route('/update_points', methods=['POST'])
def update_points():
    try:
        data = load_data()
        partecipante = request.form.get('partecipante')
        categoria = request.form.get('categoria', 'MANUALE')
        punti = int(request.form.get('punti', 0))
        note = request.form.get('note', '')

        if partecipante not in data:
            return jsonify({'status': 'error', 'message': 'Partecipante non trovato'}), 400

        data[partecipante]['punti'] += punti
        data[partecipante]['storico'].append({'categoria': categoria, 'punti': punti, 'note': note})
        save_data(data)
        return jsonify({'status': 'success', 'punti': data[partecipante]['punti']})
    except Exception as e:
        logging.exception('Errore /update_points')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/export_csv')
def export_csv():
    try:
        import csv
        data = load_data()
        with open('classifica.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Partecipante', 'Punti'])
            for p, d in data.items():
                writer.writerow([p, d['punti']])
        return "CSV esportato come classifica.csv"
    except Exception as e:
        logging.exception('Errore /export_csv')
        return f"Errore esportazione: {e}", 500

@app.errorhandler(404)
def page_not_found(e):
    return "Pagina non trovata", 404

@app.errorhandler(500)
def internal_error(e):
    logging.exception('Internal server error')
    return "Errore interno server", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

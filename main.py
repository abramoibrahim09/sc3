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
app.run(host='0.0.0.0', port=5000, debug=True)

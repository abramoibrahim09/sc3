from flask import Flask, render_template, request, redirect, url_for, jsonify
users = load_users()
if user not in users or users[user].get('role') != 'admin':
return "Accesso negato", 403
data = load_data()
# passiamo anche le categorie e i valori numerici
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
# in locale usa debug True solo per test
app.run(host='0.0.0.0', port=5000, debug=True)

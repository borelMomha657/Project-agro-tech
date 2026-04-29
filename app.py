from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Configuration de la base de données
DB_PATH = 'agro_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS collectes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  culture TEXT, prix REAL, humidite INTEGER, 
                  meteo TEXT, zone TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # Page d'accueil avec formulaire et statistiques descriptives
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM collectes", conn)
    conn.close()
    
    stats = {}
    if not df.empty:
        stats['total'] = len(df)
        stats['prix_moyen'] = round(df['prix'].mean(), 2)
        stats['humidite_moy'] = round(df['humidite'].mean(), 1)
        
    return render_template('index.html', stats=stats, data=df.to_dict(orient='records'))

@app.route('/collecte', methods=['POST'])
def collecte():
    culture = request.form.get('culture')
    prix = request.form.get('prix')
    humidite = request.form.get('humidite')
    meteo = request.form.get('meteo')
    zone = request.form.get('zone')
    
    if zone and prix:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO collectes (culture, prix, humidite, meteo, zone) VALUES (?,?,?,?,?)',
                  (culture, prix, humidite, meteo, zone))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    # Railway utilise la variable d'environnement PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

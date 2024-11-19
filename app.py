from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Route voor de loginpagina
@app.route('/')
def login():
    return render_template('login.html')  # Zorg ervoor dat login.html de juiste naam heeft

# Route voor de verwerking van het formulier
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']
    
    # Maak verbinding met de database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Zoek de gebruiker op basis van het e-mailadres
    cursor.execute("SELECT * FROM gebruikers WHERE naam = ? AND wachtwoord = ?", (email, password))
    user = cursor.fetchone()  # Haal de eerste overeenkomende gebruiker op

    # Controleer of de gebruiker bestaat
    if user:
        return redirect(url_for('dashboard'))  # Als de gebruiker gevonden is, stuur door naar dashboard
    else:
        return "Invalid credentials, try again."  # Als de gegevens niet kloppen

# Route voor het dashboard (na succesvolle login)
@app.route('/dashboard')
def dashboard():
    return "Welcome to your dashboard!"

if __name__ == '__main__':
    app.run(debug=True)

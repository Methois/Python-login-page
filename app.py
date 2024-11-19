from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

# Stel een geheime sleutel in voor sessies
app.secret_key = 'je-geheime-sleutel'  # Pas dit aan naar iets unieks en veiligs

# Route voor de loginpagina (GET)
@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')  # Zorg ervoor dat login.html de juiste naam heeft

# Route voor de verwerking van het loginformulier (POST)
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']
    
    # Maak verbinding met de database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Zoek de gebruiker op basis van het e-mailadres en wachtwoord
    cursor.execute("SELECT * FROM gebruikers WHERE naam = ? AND wachtwoord = ?", (email, password))
    user = cursor.fetchone()  # Haal de eerste overeenkomende gebruiker op

    # Controleer of de gebruiker bestaat
    if user:
        session['user_id'] = user[0]  # Bewaar de gebruikers-ID in de sessie
        session['email'] = email  # Bewaar het e-mailadres in de sessie
        return redirect(url_for('dashboard'))  # Als de gebruiker gevonden is, stuur door naar dashboard
    else:
        return "Invalid credentials, try again."  # Als de gegevens niet kloppen
    
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')  # Zorg ervoor dat signup.html de juiste naam heeft

# Route voor de verwerking van het signupformulier (POST)
@app.route('/signup', methods=['POST'])
def handle_signup():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']
    confirm_password = request.form['Confirm Wachtwoord']
    
    # Controleer of de wachtwoorden overeenkomen
    if password != confirm_password:
        return "Wachtwoorden komen niet overeen, probeer het opnieuw."
    
    # Maak verbinding met de database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Controleer of de gebruiker al bestaat
    cursor.execute("SELECT * FROM gebruikers WHERE naam = ?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        return "Dit e-mailadres is al geregistreerd."

    # Voeg de nieuwe gebruiker toe aan de database
    cursor.execute("INSERT INTO gebruikers (naam, wachtwoord) VALUES (?, ?)", (email, password))
    conn.commit()  # Bevestig de wijzigingen

    return redirect(url_for('login'))  # Stuur de gebruiker door naar de loginpagina


# Route voor het dashboard (na succesvolle login)
@app.route('/dashboard')
def dashboard():
    # Controleer of de gebruiker is ingelogd
    if 'user_id' in session:
        email = session['email']  # Haal het e-mailadres van de ingelogde gebruiker op
        return render_template('dashboard.html', email=email)  # Verstuur e-mail naar dashboardpagina
    else:
        return redirect(url_for('login'))  # Als de gebruiker niet is ingelogd, stuur door naar login

# Route voor uitloggen
@app.route('/logout')
def logout():
    session.clear()  # Verwijder alle sessiegegevens
    return redirect(url_for('login'))  # Stuur de gebruiker terug naar de loginpagina

if __name__ == '__main__':
    app.run(debug=True)

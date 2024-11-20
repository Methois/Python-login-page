from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets
import re  # Voor reguliere expressies (voor e-mailvalidatie)

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

def validate_email(email):
    """Validatie voor een geldig e-mailadres"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def validate_password(password):
    """Validatie voor een sterk wachtwoord"""
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    return True

@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gebruikers WHERE naam = ?", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['email'] = email
        return redirect(url_for('dashboard'))
    else:
        # Voeg foutmelding toe aan template
        error_message = "Invalid credentials, try again."
        return render_template('login.html', error_message=error_message)

    
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def handle_signup():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']
    confirm_password = request.form['Confirm Wachtwoord']

    if password != confirm_password:
        # Foutmelding voor niet-overeenkomende wachtwoorden
        error_message = "Wachtwoorden komen niet overeen, probeer het opnieuw."
        return render_template('signup.html', error_message=error_message)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gebruikers WHERE naam = ?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        # Foutmelding voor bestaand e-mailadres
        error_message = "Dit e-mailadres is al geregistreerd."
        return render_template('signup.html', error_message=error_message)

    hashed_password = generate_password_hash(password)

    cursor.execute("INSERT INTO gebruikers (naam, wachtwoord) VALUES (?, ?)", (email, hashed_password))
    conn.commit()

    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        email = session['email']
        return render_template('dashboard.html', email=email)
    else:
        return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    # Wachtwoordsterkte validatie voor nieuw wachtwoord
    if not validate_password(new_password):
        return "Het nieuwe wachtwoord is te zwak. Zorg voor een wachtwoord met minimaal 8 tekens, een hoofdletter, een kleine letter en een cijfer."

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gebruikers WHERE naam = ?", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[2], old_password):
        hashed_new_password = generate_password_hash(new_password)
        cursor.execute("UPDATE gebruikers SET wachtwoord = ? WHERE naam = ?", (hashed_new_password, email))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    else:
        conn.close()
        return "Oud wachtwoord is incorrect. Probeer het opnieuw."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check of de admin-account al bestaat
    cursor.execute("SELECT * FROM gebruikers WHERE naam = 'admin'")
    admin = cursor.fetchone()

    if not admin:  # Als de admin nog niet bestaat
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if username != 'admin':
                return "De gebruikersnaam moet 'admin' zijn om toegang te krijgen tot de admin-pagina."

            # Voeg de admin toe met gehashed wachtwoord
            hashed_password = generate_password_hash(password)

            cursor.execute("INSERT INTO gebruikers (naam, wachtwoord) VALUES (?, ?)", ('admin', hashed_password))
            conn.commit()

            print(f"Admin-account aangemaakt met gehasht wachtwoord: {hashed_password}")
            return redirect(url_for('admin_dashboard'))  # Ga naar de admin dashboard

        # Als de admin nog niet bestaat, toon een formulier om een admin-account aan te maken
        return render_template('create_admin.html')

    # Als de admin-account al bestaat, ga dan verder met het inlogproces
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and check_password_hash(admin[2], password):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Ongeldige admin-inloggegevens, probeer het opnieuw."

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam, wachtwoord FROM gebruikers WHERE naam != 'admin'")
    users = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/change_password/<int:user_id>', methods=['POST'])
def admin_change_password(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    new_password = request.form['new_password']
    
    # Wachtwoordsterkte validatie voor admin
    if not validate_password(new_password):
        return "Het nieuwe wachtwoord is te zwak. Zorg voor een wachtwoord met minimaal 8 tekens, een hoofdletter, een kleine letter en een cijfer."
    
    hashed_new_password = generate_password_hash(new_password)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE gebruikers SET wachtwoord = ? WHERE id = ?", (hashed_new_password, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gebruikers WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)

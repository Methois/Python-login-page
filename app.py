from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

app.secret_key = 'je-geheime-sleutel'

# Route voor de loginpagina (GET)
@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gebruikers WHERE naam = ? AND wachtwoord = ?", (email, password))
    user = cursor.fetchone() 

    if user:
        session['user_id'] = user[0] 
        session['email'] = email 
        return redirect(url_for('dashboard')) 
    else:
        return "Invalid credentials, try again." 
    
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html') 

@app.route('/signup', methods=['POST'])
def handle_signup():
    email = request.form['E-mail adres']
    password = request.form['Wachtwoord']
    confirm_password = request.form['Confirm Wachtwoord']

    if password != confirm_password:
        return "Wachtwoorden komen niet overeen, probeer het opnieuw."

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gebruikers WHERE naam = ?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        return "Dit e-mailadres is al geregistreerd."

    cursor.execute("INSERT INTO gebruikers (naam, wachtwoord) VALUES (?, ?)", (email, password))
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

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gebruikers WHERE email = ? AND wachtwoord = ?", (email, old_password))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE gebruikers SET wachtwoord = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard')) 
    else:
        conn.close()
        return "Incorrect current password. Try again."

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Controleer admin-gegevens
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials, try again."
    return render_template('admin_login.html')

# Route voor het admin-dashboard
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

# Route voor het wijzigen van wachtwoorden door de admin
@app.route('/admin/change_password/<int:user_id>', methods=['POST'])
def admin_change_password(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    new_password = request.form['new_password']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE gebruikers SET wachtwoord = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))


# Route voor het verwijderen van gebruikers
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

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)

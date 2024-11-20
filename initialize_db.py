import sqlite3

# Verbind met de database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Maak de tabel 'gebruikers' als deze niet bestaat
cursor.execute('''
CREATE TABLE IF NOT EXISTS gebruikers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    wachtwoord TEXT NOT NULL
)
''')

# Voeg een admin-gebruiker toe
cursor.execute("INSERT INTO gebruikers (naam, wachtwoord) VALUES (?, ?)", ('admin', 'admin'))

conn.commit()
conn.close()

print("Database geinitialiseerd met admin-gebruiker.")

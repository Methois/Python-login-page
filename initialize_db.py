import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Maak de tabel 'gebruikers' als deze nog niet bestaat
    cursor.execute('''CREATE TABLE IF NOT EXISTS gebruikers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        naam TEXT NOT NULL,
                        wachtwoord TEXT NOT NULL)''')

    # Maak de tabel 'admin' als deze nog niet bestaat (optioneel, bijvoorbeeld voor later gebruik)
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        wachtwoord TEXT NOT NULL)''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database en tabellen zijn succesvol aangemaakt!")

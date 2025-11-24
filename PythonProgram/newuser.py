#Tworzenie nowego usera
import mysql.connector
from db_config import config
import bcrypt

### NEW USER

def new_user(username, password):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        print(f"Użytkownik '{username}' poprawnie zarejestrowany!")
    except mysql.connector.Error as e:
        print("Błąd: ", e)
    finally:
        cursor.close()
        conn.close()

current_user, current_role = None, None

current_role = 'admin'  # TO PÓŹNIEJ USUŃ, NA RAZIE WSTAWIONE ŻEBY SPRAWDZIĆ CZY DZIAŁA -> DZIAŁA

if current_role == 'admin':
    new_username = input("Podaj login nowego użytkownika: ")
    new_password = input("Podaj hasło nowego użytkownika: ")
    new_user(new_username, new_password)
else:
    print("Nie masz uprawnień do tworzenia nowych użytkowników!")

#### ZMIANA HASŁA

def change_password(username, new_password):
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s", (password_hash, username)
        )
        conn.commit()
        print(f"Hasło '{username}' zostało zmienione.")
    except mysql.connector.Error as e:
        print("Error: ", e)
    finally:
        cursor.close()
        conn.close()

### USER DEACTIVATION

def deactivate_user(username):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET active = 0 WHERE username = %s", (username,))
        conn.commit()
        print(f"The user '{username}' has been deactivated.")
    except mysql.connector.Error as e:
        print("Error: ", e)
    finally:
        cursor.close()
        conn.close()
#Tworzenie nowego usera
import mysql.connector
from db_config import config
import bcrypt


current_user, current_role = login_user()

if current_role == 'admin':
    new_username = input("Podaj login nowego użytkownika: ")
    new_password = input("Podaj hasło nowego użytkownika: ")
    new_user(new_username, new_password)
else:
    print("Nie masz uprawnień do tworzenia nowych użytkowników!")

def new_user(username, password):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        print(f"Użytkownik '{username}' poprawnie zarejestrowany!")
    except mysql.connector.Error as e:
        print("Błąd: ", e)
    finally:
        cursor.close()
        conn.close()
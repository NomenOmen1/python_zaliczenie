#LOGIN

# haslo = "1234"
# current_user = None
#
# while True:
#     login = input("Podaj login: ")
#     podane_haslo = input("Podaj hasło: ")
#     if haslo == podane_haslo:
#         print(f"Sukces! Zalogowano poprawnie, witaj {login}!")
#         break
#     else:
#         print(f"Hasło do systemu niepoprawne.")



#Tworzenie nowego usera
import mysql.connector
from db_config import config
import bcrypt

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


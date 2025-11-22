#Zarys planu:
# 1. wgrywanie plików csv do bazy danych
# 2. odpalam data quality rules które sprawdzają dane znajdujace sie w bazie danych
# 3. zapisuje wyniki testow (KPI)
# 4.prosty interfejs

# import pandas as pd
# import mysql.connector
# from mysql.connector import Error
#
# config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '1234',
#     'database': 'data_quality_db'
# }
#
# def load_csv_to_db(csv_file, table_name):
#     try:
#         df = pd.read_csv(csv_file, encoding='cp1250')
#         print(f"Wczytano {len(df)} wierszy z {csv_file}.")
#         print(df.head())
#         print(df.columns)
#
#         conn = mysql.connector.connect(**config)
#         cursor = conn.cursor()
#
#         for _, row in df.iterrows():
#             placeholders = ', '.join(['%s'] * len(row))
#             columns = ', '.join(row.index)
#             sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
#             cursor.execute(sql, tuple(row))
#
#             update_stmt = ', '.join([f"{col}=VALUES({col})" for col in df.columns if col != 'id'])
#
#         conn.commit()
#         print(f"Pomyślnie zapisano do tabeli {table_name}!")
#
#     except Error as e:
#         print("Błąd MySQL:", e)
#
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             cursor.close()
#             conn.close()
#             print("Połączenie z bazą zamknięte.")
#
# if __name__ == "__main__":
#     load_csv_to_db("data_input.csv", "customers")


import pandas as pd
import mysql.connector
from mysql.connector import Error

# konfiguracja połączenia z MySQL
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'data_quality_db'
}

def load_csv_to_db(csv_file, table_name):
    try:
        # Wczytanie CSV
        df = pd.read_csv(csv_file, encoding='cp1250')
        print(f"Wczytano {len(df)} wierszy z {csv_file}.")

        # Oczyszczenie nazw kolumn (usuń średniki i spacje)
        df.columns = [col.strip().replace(';','') for col in df.columns]

        # Oczyszczenie wszystkich wartości w DataFrame
        df = df.applymap(lambda x: str(x).replace(';','') if isinstance(x, str) else x)

        print(df.head())
        print("Kolumny:", df.columns)

        # Połączenie z bazą danych
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(row))

            # Tworzymy ON DUPLICATE KEY UPDATE dla wszystkich kolumn poza 'id'
            update_stmt = ', '.join([f"{col}=VALUES({col})" for col in df.columns if col != 'id'])

            sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_stmt};
            """

            cursor.execute(sql, tuple(row))

        conn.commit()
        print(f"Pomyślnie zapisano lub zaktualizowano {len(df)} wierszy w tabeli {table_name}!")

    except Error as e:
        print("Błąd MySQL:", e)

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Połączenie z bazą zamknięte.")

if __name__ == "__main__":
    load_csv_to_db("data_input.csv", "customers")




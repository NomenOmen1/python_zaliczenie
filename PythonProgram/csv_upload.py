import pandas as pd
import mysql.connector
from mysql.connector import Error
import configparser
from db_config import config

def load_csv_to_db(csv_file, table_name):
    log = []
    try:
        df = pd.read_csv(csv_file, encoding='cp1250')
        print(f"Wczytano {len(df)} wierszy z {csv_file}.")

        df.columns = [col.strip().replace(';','') for col in df.columns]

        df = df.map(lambda x: str(x).replace(';','') if isinstance(x, str) else x)

        print(df)
        print("Kolumny:", df.columns)

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(row))

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
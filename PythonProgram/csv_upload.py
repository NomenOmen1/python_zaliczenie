import pandas as pd
import mysql.connector
from mysql.connector import Error
from db_config import config
from tkinter import messagebox  # jeśli chcesz komunikat w GUI

def load_csv_and_log(csv_file, table_name, username):

    log = []
    try:
        df = pd.read_csv(csv_file, encoding='cp1250')
        row_count = len(df)
        log.append(f"Loaded {row_count} rows from {csv_file}.")

        df.columns = [col.strip().replace(';','') for col in df.columns]
        df = df.map(lambda x: str(x).replace(';','') if isinstance(x, str) else x)

        log.append(f"Columns: {list(df.columns)}")

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
        log.append(f"The data has been uploaded into {table_name} successfully! \nTotal rows: {row_count}")

        cursor.execute("""
            INSERT INTO data_load_log (table_name, file_name, row_count, loaded_by)
            VALUES (%s, %s, %s, %s)
        """, (table_name, csv_file, row_count, username))
        conn.commit()
        log.append(f"The Log has been saved into data_load_log table")

        messagebox.showinfo("Info", f"CSV file has been uploaded and logged! Total rows: {row_count}")

    except Error as e:
        log.append(f"Błąd MySQL: {e}")
        messagebox.showerror("Error", f"The following error occured: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            log.append("Connection with DB closed.")

    return "\n".join(log)

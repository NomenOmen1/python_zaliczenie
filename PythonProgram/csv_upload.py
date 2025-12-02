import pandas as pd
import mysql.connector
from mysql.connector import Error
from db_config import config
from tkinter import messagebox  # jeśli chcesz komunikat w GUI


import pandas as pd
import mysql.connector
from mysql.connector import Error
from db_config import config
from tkinter import messagebox
import os

def load_csv_and_log(csv_file, table_name, username):
    log = []
    success = True
    error_shown = False
    filename_only = os.path.basename(csv_file)

    try:
        df = pd.read_csv(filename_only, sep=None, engine='python', encoding='cp1250')
        row_count = len(df)
        log.append(f"Loaded {row_count} rows from {filename_only}.")

        df.columns = [col.strip().replace(';','') for col in df.columns]
        df = df.apply(lambda col: col.str.replace(';','', regex=False) if col.dtype == 'object' else col)
        log.append(f"Columns: {list(df.columns)}")

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            try:
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
            except Error as e:
                success = False
                log.append(f"SQL error in row: {row.to_dict()}")
                log.append(str(e))
                if not error_shown:
                    messagebox.showerror("Error", f"SQL error in a row:\n{e}")
                    error_shown = True
                break

        if success:
            try:
                cursor.execute("""
                    INSERT INTO data_load_log (table_name, file_name, row_count, loaded_by)
                    VALUES (%s, %s, %s, %s)
                """, (table_name, filename_only, row_count, username))
                conn.commit()
                log.append("The log entry has been saved in data_load_log.")
            except Error as e:
                success = False
                log.append(f"MySQL error when inserting into data_load_log: {e}")
                if not error_shown:
                    messagebox.showerror("Error", f"Error inserting into data_load_log:\n{e}")
                    error_shown = True

    except Exception as e:
        success = False
        log.append(f"Critical error: {e}")
        if not error_shown:
            messagebox.showerror("Error", f"The following error occurred:\n{e}")
            error_shown = True

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            log.append("Connection with DB closed.")

    return "\n".join(log), success  # <-- zwracamy log i flagę sukcesu




# def load_csv_and_log(csv_file, table_name, username):
#
#     log = []
#     success = True
#     try:
#         df = pd.read_csv(csv_file, sep=None, engine='python', encoding='cp1250')
#         row_count = len(df)
#         log.append(f"Loaded {row_count} rows from {csv_file}.")
#
#         df.columns = [col.strip().replace(';','') for col in df.columns]
#         #df = df.map(lambda x: str(x).replace(';','') if isinstance(x, str) else x)
#         df = df.apply(lambda col: col.str.replace(';','', regex=False) if col.dtype == 'object' else col)
#
#         log.append(f"Columns: {list(df.columns)}")
#
#         conn = mysql.connector.connect(**config)
#         cursor = conn.cursor()
#
#         for _, row in df.iterrows():
#             columns = ', '.join(df.columns)
#             placeholders = ', '.join(['%s'] * len(row))
#             update_stmt = ', '.join([f"{col}=VALUES({col})" for col in df.columns if col != 'id'])
#             sql = f"""
#             INSERT INTO {table_name} ({columns})
#             VALUES ({placeholders})
#             ON DUPLICATE KEY UPDATE {update_stmt};
#             """
#             cursor.execute(sql, tuple(row))
#
#         conn.commit()
#         log.append(f"The data has been uploaded into {table_name} successfully! \nTotal rows: {row_count}")
#
#         cursor.execute("""
#             INSERT INTO data_load_log (table_name, file_name, row_count, loaded_by)
#             VALUES (%s, %s, %s, %s)
#         """, (table_name, csv_file, row_count, username))
#         conn.commit()
#         log.append(f"The Log has been saved into data_load_log table")
#
#         #messagebox.showinfo("Info", f"CSV file has been uploaded and logged! Total rows: {row_count}")
#
#     except Error as e:
#         success = False
#         log.append(f"MySQL Error: {e}")
#         messagebox.showerror("Error", f"The following error occured: {e}")
#
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             cursor.close()
#             conn.close()
#             log.append("Connection with DB closed.")
#
#         if success:
#             messagebox.showinfo("Info", f"CSV file has been uploaded and logged! Total rows: {row_count}")
#
#     return "\n".join(log)

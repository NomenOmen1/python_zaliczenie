import pandas as pd
import mysql.connector
from mysql.connector import Error
import datetime

#kolumny w dq_rules : id, status, created_at, activated_at, version, description, rule_type, rule_params, sql_query

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'data_quality_db'
}

#Dane do insert do db

time_now = datetime.datetime.now()
created_at = time_now.strftime("%Y-%m-%d %H:%M")
print(created_at)




#
# def load_csv_to_db(csv_file, table_name):
#     try:
#         df = pd.read_csv(csv_file, encoding='cp1250')
#         print(f"Wczytano {len(df)} wierszy z {csv_file}.")
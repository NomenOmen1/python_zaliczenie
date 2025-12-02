import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import config
import time
import json

import tkinter as tk

class CheckDqPanel:
    def __init__(self, root, username, role, data_quality_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.data_quality_root = data_quality_root
        self.time_var = time_var

        self.root.title("DQ Panel")
        self.root.geometry("800x400")

        # Label z użytkownikiem
        tk.Label(self.root, text=f"Logged in as: {self.username}", anchor="e").pack(fill="x", padx=10, pady=5)

        # Zegar
        self.clock_label = tk.Label(self.root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        # Przycisk powrotu
        tk.Button(self.root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

        #FRAME
        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=10, fill="x")

        button1 = tk.Button(top_frame, text="Run DQ Rule", command=self.run_dq_check).pack(padx=10, pady=5)
        button2 = tk.Button(top_frame, text="Zmień Hasło")
        button3 = tk.Button(top_frame, text="Deactivate User")

        button1.grid(row=0, column=0, sticky="nsew")
        button2.grid(row=0, column=1, sticky="nsew")
        button3.grid(row=0, column=2, sticky="nsew")

        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=1)

    def go_back(self):
        self.root.destroy()
        self.data_quality_root.deiconify()

class DQRunner:
    def __init__(self, rule_id):
        self.rule_id = rule_id
        self.sql_query = None
        self.rule_version = None

    def load_rule(self):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM dq_rules WHERE rule_id = {self.rule_id}", (self.rule_id))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            raise ValueError(f"Rule ID {self.rule_id} does not exist or is inactive.")
        self.sql_query, self.rule_version = row

    def run_dq_check(self):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(self.sql_query)
        results = cursor.fetchall()

        failed_count = len(results)

        cursor.execute("Select Count(*) as total from customers")
        total_count = cursor.fetchone()["total"]
        passed_count = total_count - failed_count
        kpi = round(passed_count / total_count, 2)

        cursor.close()
        conn.close()

        return {
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "failed_count": failed_count,
            "passed_count": passed_count,
            "sample_failed_records": sample_failed_records,
            "timestamp": datetime.now()
        }

    def save_dq_check_result(self):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("""
                    INSERT INTO dq_results
                    (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
            result["rule_id"],
            result["rule_version"],
            result["failed_count"],
            result["passed_count"],
            result["sample_failed_records"],
            result["timestamp"]
        ))
        conn.commit()
        cursor.close()
        conn.close()

    def execute_dq_check(self):
        self.load_rule()
        result = self.run_dq_check()
        self.save_dq_check_result()
        return result



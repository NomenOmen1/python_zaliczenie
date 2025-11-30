import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from db_config import config
import json
from datetime import datetime
import csv
import os
from utils import place_window

class CheckDqPanel:
    def __init__(self, root, username, role, data_quality_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.data_quality_root = data_quality_root
        self.time_var = time_var

        self.root.title("DQ Panel")
        #self.root.geometry("800x400")
        place_window(self.root, width=800, height=400)

        tk.Label(self.root, text=f"Logged in as: {self.username}", anchor="e").pack(fill="x", padx=10, pady=5)
        self.clock_label = tk.Label(self.root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)
        tk.Button(self.root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=10, fill="x")

        tk.Button(top_frame, text="Run DQ Check", command=self.open_dq_dialog).grid(row=0, column=0, sticky="nsew")
        tk.Button(top_frame, text="Choose DQ Rule", command=self.get_tables_to_dq_check).grid(row=0, column=1, sticky="nsew")
        tk.Button(top_frame, text="Deactivate User").grid(row=0, column=2, sticky="nsew")

        for i in range(3):
            top_frame.grid_columnconfigure(i, weight=1)

    def go_back(self):
        self.root.destroy()
        self.data_quality_root.deiconify()

    def get_tables_to_dq_check(self):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

        excluded = {"dq_rules", "dq_rules_history", "data_load_log", "dq_results", "dq_field_results"}
        return [t for t in all_tables if t not in excluded]

    def get_active_rules_for_table(self, table_name):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM dq_rules WHERE status='ACTIVE' AND target_table=%s", (table_name,))
        rules = [r[0] for r in cursor.fetchall()]  # tylko id
        cursor.close()
        conn.close()
        return rules

    def open_dq_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Run DQ Rules")
        dialog.geometry("400x300")

        # Dropdown tabel
        available_tables = self.get_tables_to_dq_check()
        self.selected_table = tk.StringVar(value=available_tables[0] if available_tables else "")
        tk.Label(dialog, text="Select table to check:").pack(pady=5)
        table_dropdown = ttk.Combobox(dialog, values=available_tables, textvariable=self.selected_table, state="readonly")
        table_dropdown.pack(pady=5)

        # Wybór typu uruchomienia
        tk.Label(dialog, text="Choose run type:").pack(pady=10)
        self.run_type = tk.StringVar(value="single")
        tk.Radiobutton(dialog, text="Single Rule", variable=self.run_type, value="single").pack()
        tk.Radiobutton(dialog, text="All Rules", variable=self.run_type, value="all").pack()

        # Dropdown dla pojedynczej reguły
        self.rule_var = tk.IntVar()
        self.rule_dropdown = tk.OptionMenu(dialog, self.rule_var, [])
        self.rule_dropdown.pack(pady=10)

        def update_rules(*args):
            table = self.selected_table.get()
            rules = self.get_active_rules_for_table(table)
            menu = self.rule_dropdown["menu"]
            menu.delete(0, "end")
            if rules:
                self.rule_var.set(rules[0])
                for r in rules:
                    menu.add_command(label=r, command=lambda value=r: self.rule_var.set(value))

                else:
                    self.rule_var.set(0)

        update_rules()

        self.selected_table.trace_add("write", lambda *args: update_rules())

        tk.Button(dialog, text="Run", command=lambda: self.run_dq_from_dialog(dialog)).pack(pady=10)

    def run_dq_from_dialog(self, dialog):
        table = self.selected_table.get()
        run_type = self.run_type.get()
        dialog.destroy()

        if run_type == "all":
            self.run_all_dq_rules(table)
        else:
            rule_id = self.rule_var.get()
            if rule_id == 0:
                messagebox.showerror("Error", "No rule selected.")
                return
            self.run_selected_dq_rule(table, rule_id)

    def run_all_dq_rules(self, table):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, sql_query, version FROM dq_rules WHERE status='ACTIVE' AND target_table=%s",
            (table,)
        )
        rules = cursor.fetchall()
        if not rules:
            messagebox.showinfo("Info", f"No active rules for table {table}.")
            cursor.close()
            conn.close()
            return

        results_summary = []
        for rule in rules:
            rule_id = rule['id']
            sql_query = rule['sql_query']
            rule_version = rule['version']

            # Obsługa błędów SQL
            try:
                cursor.execute(sql_query)
                failed_records = cursor.fetchall()
            except mysql.connector.Error as e:
                messagebox.showerror("SQL Error", f"Error executing rule {rule_id}:\n{e}")
                continue  # przejdź do kolejnej reguły

            failed_count = len(failed_records)

            # Liczba wszystkich rekordów w tabeli
            try:
                cursor.execute(f"SELECT COUNT(*) as total FROM {table}")
                total_count = cursor.fetchone()["total"]
            except mysql.connector.Error as e:
                messagebox.showerror("SQL Error", f"Error counting records in table {table}:\n{e}")
                continue

            passed_count = total_count - failed_count

            sample_failed_records = json.dumps(failed_records[:5])
            timestamp = datetime.now()

            try:
                cursor.execute(
                    """
                    INSERT INTO dq_results
                    (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
                )
            except mysql.connector.Error as e:
                messagebox.showerror("SQL Error", f"Error inserting DQ results for rule {rule_id}:\n{e}")
                continue

            results_summary.append(f"Rule {rule_id}: Passed {passed_count}, Failed {failed_count}")

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("DQ Results", "\n".join(results_summary))

    def run_selected_dq_rule(self, table, rule_id):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        # Pobranie zapytania i wersji reguły
        cursor.execute(
            "SELECT sql_query, version FROM dq_rules WHERE id=%s AND status='ACTIVE'",
            (rule_id,)
        )
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", f"Rule {rule_id} not found or inactive.")
            cursor.close()
            conn.close()
            return

        sql_query, rule_version = row  # <-- dokładnie taka wersja, jak w tabeli

        try:
            cursor.execute(sql_query)
            records = cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror("SQL Error", f"Error executing rule {rule_id}:\n{e}")
            cursor.close()
            conn.close()
            return

        timestamp = datetime.now()
        failed_count = 0
        passed_count = 0

        # Wstawienie wyników do dq_field_results
        for record in records:
            record_id = record.get('id', '')  # lub inna kolumna identyfikująca rekord
            for field_name, field_value in record.items():
                test_result = record.get('dq_check', 1)  # 0 = fail, 1 = pass
                if test_result == 0:
                    failed_count += 1
                else:
                    passed_count += 1
                error_message = record.get('error_message', '') if test_result == 0 else ''
                cursor.execute(
                    """
                    INSERT INTO dq_field_results
                    (rule_id, rule_version, record_id, field_name, field_value, test_result, error_message, timestamp, target_table)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (rule_id, rule_version, str(record_id), field_name, str(field_value),
                     test_result, error_message, timestamp, table)
                )

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("DQ Result", f"Rule {rule_id} executed.\nPassed: {passed_count}, Failed: {failed_count}")

    def run_active_dq_rules_and_export_csv(self, output_dir="dq_errors_csv"):
        os.makedirs(output_dir, exist_ok=True)
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT id, version, target_table, sql_query FROM dq_rules WHERE status='ACTIVE'")
            rules = cursor.fetchall()
            if not rules:
                print("No active rules found.")
                return

            for rule in rules:
                rule_id = rule['id']
                rule_version = rule['version']
                table = rule['target_table']
                sql_query = rule['sql_query']

                cursor.execute(sql_query)
                records = cursor.fetchall()
                failed_records = [r for r in records if r.get('dq_check') == 0]
                passed_records = [r for r in records if r.get('dq_check') == 1]

                failed_count = len(failed_records)
                passed_count = len(passed_records)

                cursor.execute("""
                    INSERT INTO dq_results
                    (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (rule_id, rule_version, failed_count, passed_count, json.dumps(failed_records[:5]), datetime.now()))

                if failed_records:
                    csv_file = os.path.join(output_dir, f"rule_{rule_id}_errors.csv")
                    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=failed_records[0].keys())
                        writer.writeheader()
                        writer.writerows(failed_records)
                    print(f"Rule {rule_id} - {failed_count} failed records exported to {csv_file}")

            conn.commit()
            print("All active DQ rules executed and results exported.")
        finally:
            cursor.close()
            conn.close()

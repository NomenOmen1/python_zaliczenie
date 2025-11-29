import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import mysql.connector
from db_config import config
import json
from datetime import datetime

class CheckDqPanel:
    def __init__(self, root, username, role, data_quality_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.data_quality_root = data_quality_root
        self.time_var = time_var

        self.root.title("DQ Panel")
        self.root.geometry("800x400")

        #Label z użytkownikiem
        tk.Label(self.root, text=f"Logged in as: {self.username}", anchor="e").pack(fill="x", padx=10, pady=5)
        # ZEGAR
        self.clock_label = tk.Label(self.root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)
        #PRZYCISK POWROTU
        tk.Button(self.root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=10, fill="x")

        tk.Button(top_frame, text="Run DQ Check", command=self.open_dq_dialog).grid(row=0, column=0, sticky="nsew")
        tk.Button(top_frame, text="Choose DQ Rule", command=self.ask_table_to_check).grid(row=0, column=1, sticky="nsew")
        tk.Button(top_frame, text="Deactivate User").grid(row=0, column=2, sticky="nsew")

        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=1)

        # Tu możesz zrobić dropdown z listą reguł
        self.rule_id_var = tk.IntVar(value=1)
        self.rule_dropdown = tk.OptionMenu(self.root, self.rule_id_var, *self.get_active_rules())
        self.rule_dropdown.pack(pady=10)

    def go_back(self):
        self.root.destroy()
        self.data_quality_root.deiconify()

    # def get_active_rules(self):
    #     conn = mysql.connector.connect(**config)
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT id FROM dq_rules WHERE status='ACTIVE'")
    #     rules = [r[0] for r in cursor.fetchall()]
    #     cursor.close()
    #     conn.close()
    #     return rules
    #
    # def run_all_dq_rules(self):
    #     conn = mysql.connector.connect(**config)
    #     cursor = conn.cursor(dictionary=True)
    #
    #     cursor.execute("SELECT id, sql_query, version FROM dq_rules WHERE status='ACTIVE'")
    #     rules = cursor.fetchall()
    #     if not rules:
    #         messagebox.showinfo("Info", "No active rules found.")
    #         cursor.close()
    #         conn.close()
    #         return
    #
    #     results_summary = []
    #
    #     for rule in rules:
    #         rule_id = rule['id']
    #         sql_query = rule['sql_query']
    #         rule_version = rule['version']
    #
    #         cursor.execute(sql_query)
    #         failed_records = cursor.fetchall()
    #         failed_count = len(failed_records)
    #
    #         cursor.execute("SELECT COUNT(*) as total FROM customers")
    #         total_count = cursor.fetchone()["total"]
    #         passed_count = total_count - failed_count
    #
    #         sample_failed_records = json.dumps(failed_records[:5])
    #         timestamp = datetime.now()
    #
    #         cursor.execute("""
    #             INSERT INTO dq_results
    #             (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
    #             VALUES (%s, %s, %s, %s, %s, %s)
    #         """, (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp))
    #
    #         results_summary.append(f"Rule {rule_id}: Passed {passed_count}, Failed {failed_count}")
    #
    #     conn.commit()
    #     cursor.close()
    #     conn.close()
    #
    #     messagebox.showinfo("DQ Results", "\n".join(results_summary))
    #
    # def run_selected_dq_rule(self):
    #     rule_id = self.rule_id_var.get()
    #     conn = mysql.connector.connect(**config)
    #     cursor = conn.cursor(dictionary=True)
    #
    #     cursor.execute("SELECT sql_query, version FROM dq_rules WHERE id=%s AND status='ACTIVE'", (rule_id,))
    #     row = cursor.fetchone()
    #     if not row:
    #         messagebox.showerror("Error", f"Rule {rule_id} not found or inactive.")
    #         cursor.close()
    #         conn.close()
    #         return
    #
    #     sql_query, rule_version = row
    #
    #     cursor.execute(sql_query)
    #     failed_records = cursor.fetchall()
    #     failed_count = len(failed_records)
    #
    #     cursor.execute("SELECT COUNT(*) as total FROM customers")
    #     total_count = cursor.fetchone()["total"]
    #     passed_count = total_count - failed_count
    #
    #     sample_failed_records = json.dumps(failed_records[:5])
    #     timestamp = datetime.now()
    #
    #     cursor.execute("""
    #         INSERT INTO dq_results
    #         (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
    #         VALUES (%s, %s, %s, %s, %s, %s)
    #     """, (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp))
    #
    #     conn.commit()
    #     cursor.close()
    #     conn.close()
    #
    #     messagebox.showinfo("DQ Result", f"Rule {rule_id} executed.\nPassed: {passed_count}, Failed: {failed_count}")
    #
    # def ask_table_to_check(self):
    #     # Lista dostępnych tabel
    #     available_tables = ["customers", "orders", "products", "employees"]
    #
    #     # Tworzymy nowe okno dialogowe
    #     dialog = tk.Toplevel(self.root)
    #     dialog.title("Select Table")
    #     dialog.geometry("300x150")
    #     tk.Label(dialog, text="Select table to check:").pack(pady=10)
    #
    #     table_var = tk.StringVar(value=available_tables[0])
    #     dropdown = tk.OptionMenu(dialog, table_var, *available_tables)
    #     dropdown.pack(pady=5)
    #
    #     def on_confirm():
    #         selected_table = table_var.get()
    #         dialog.destroy()
    #         self.run_dq_for_table(selected_table)
    #
    #     tk.Button(dialog, text="OK", command=on_confirm).pack(pady=10)

    def open_dq_dialog(self):
        # Okno dialogowe obok głównego
        dialog = tk.Toplevel(self.root)
        dialog.title("Run DQ Rules")
        dialog.geometry("400x300")

        tk.Label(dialog, text="Select table to check:").pack(pady=10)
        available_tables = ["customers", "orders", "products", "employees"]  # możesz pobrać dynamicznie
        self.selected_table = tk.StringVar(value=available_tables[0])
        tk.OptionMenu(dialog, self.selected_table, *available_tables).pack(pady=5)

        # Wybór pojedynczego rule lub wszystkich
        tk.Label(dialog, text="Choose run type:").pack(pady=10)
        self.run_type = tk.StringVar(value="single")
        tk.Radiobutton(dialog, text="Single Rule", variable=self.run_type, value="single").pack()
        tk.Radiobutton(dialog, text="All Rules", variable=self.run_type, value="all").pack()

        # Dropdown dla pojedynczego rule (aktualizowany dynamicznie)
        self.rule_var = tk.IntVar()
        self.rule_dropdown = tk.OptionMenu(dialog, self.rule_var, [])
        self.rule_dropdown.pack(pady=10)

        def update_rules(*args):
            table = self.selected_table.get()
            rules = self.get_active_rules_for_table(table)
            self.rule_var.set(rules[0] if rules else 0)
            menu = self.rule_dropdown["menu"]
            menu.delete(0, "end")
            for r in rules:
                menu.add_command(label=r, command=lambda value=r: self.rule_var.set(value))

        self.selected_table.trace_add("write", update_rules)
        update_rules()

        tk.Button(dialog, text="Run", command=lambda: self.run_dq_from_dialog(dialog)).pack(pady=10)

    def get_active_rules_for_table(self, table_name):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM dq_rules WHERE status='ACTIVE' AND rule_type=%s", (table_name,))
        rules = [r[0] for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return rules

    def run_dq_from_dialog(self, dialog):
        table = self.selected_table.get()
        run_type = self.run_type.get()
        dialog.destroy()

        if run_type == "all":
            self.run_all_dq_rules(table)
        else:
            rule_id = self.rule_var.get()
            self.run_selected_dq_rule(table, rule_id)

    def run_all_dq_rules(self, table):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, sql_query, version FROM dq_rules WHERE status='ACTIVE' AND rule_type=%s", (table,))
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

            cursor.execute(sql_query)
            failed_records = cursor.fetchall()
            failed_count = len(failed_records)

            cursor.execute(f"SELECT COUNT(*) as total FROM {table}")
            total_count = cursor.fetchone()["total"]
            passed_count = total_count - failed_count

            sample_failed_records = json.dumps(failed_records[:5])
            timestamp = datetime.now()

            cursor.execute("""
                INSERT INTO dq_results
                (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp))

            results_summary.append(f"Rule {rule_id}: Passed {passed_count}, Failed {failed_count}")

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("DQ Results", "\n".join(results_summary))

    def run_selected_dq_rule(self, table, rule_id):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT sql_query, version FROM dq_rules WHERE id=%s AND status='ACTIVE'", (rule_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", f"Rule {rule_id} not found or inactive.")
            cursor.close()
            conn.close()
            return

        sql_query, rule_version = row
        cursor.execute(sql_query)
        failed_records = cursor.fetchall()
        failed_count = len(failed_records)

        cursor.execute(f"SELECT COUNT(*) as total FROM {table}")
        total_count = cursor.fetchone()["total"]
        passed_count = total_count - failed_count

        sample_failed_records = json.dumps(failed_records[:5])
        timestamp = datetime.now()

        cursor.execute("""
            INSERT INTO dq_results
            (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rule_id, rule_version, failed_count, passed_count, sample_failed_records, timestamp))

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("DQ Result", f"Rule {rule_id} executed.\nPassed: {passed_count}, Failed: {failed_count}")
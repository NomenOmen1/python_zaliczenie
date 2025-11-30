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
        # POTESTUJ TO BO FAJNIE GDYBY DZIAŁAŁO ! place_window(self.root, width=400, height=300)

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

                if not rules:
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
        all_records_for_csv = []

        try:
            # Pobranie aktywnych reguł
            cursor.execute(
                "SELECT id, sql_query, version, target_table, error_message "
                "FROM dq_rules WHERE status='ACTIVE' AND target_table=%s",
                (table,)
            )
            rules = cursor.fetchall()

            if not rules:
                messagebox.showinfo("Info", f"No active rules for table {table}.")
                return

            total_rules = len(rules)
            rules_executed = 0
            results_summary = []

            for rule in rules:
                rule_id = rule['id']
                sql_query = rule['sql_query']
                rule_version = rule['version']
                table = rule['target_table']
                rule_error_message = rule.get('error_message') or "DQ check failed"

                # Wykonanie zapytania SQL reguły
                try:
                    cursor.execute(sql_query)
                    records = cursor.fetchall()
                except mysql.connector.Error as e:
                    messagebox.showerror("SQL Error", f"Error executing rule {rule_id}:\n{e}")
                    continue

                if not records:
                    messagebox.showinfo("Info", f"Rule {rule_id} returned no records.")
                    continue

                # Liczymy passed i failed
                failed_count = sum(1 for r in records if r.get('dq_check', 1) == 0)
                passed_count = sum(1 for r in records if r.get('dq_check', 1) == 1)

                # Wstawienie do dq_results
                try:
                    cursor.execute(
                        """
                        INSERT INTO dq_results
                        (rule_id, rule_version, failed_count, passed_count)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (rule_id, rule_version, failed_count, passed_count)
                    )
                except mysql.connector.Error as e:
                    messagebox.showerror("SQL Error", f"Error inserting DQ results for rule {rule_id}:\n{e}")
                    continue

                # Wstawienie do dq_field_results i przygotowanie rekordów do CSV
                for record in records:
                    record_id = str(record.get('id', 'unknown'))
                    test_result = record.get('dq_check', 1)
                    message = "DQ check passed" if test_result == 1 else rule_error_message

                    checked_field_name = list(record.keys())[1]
                    field_value = record.get(checked_field_name, "")

                    try:
                        cursor.execute(
                            """
                            INSERT INTO dq_field_results
                            (rule_id, rule_version, record_id, field_name, field_value, test_result, error_message, target_table)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                            """,
                            (
                                rule_id,
                                rule_version,
                                record_id,
                                checked_field_name,
                                str(field_value) if field_value is not None else "",
                                test_result,
                                message,
                                table
                            )
                        )
                    except mysql.connector.Error as e:
                        messagebox.showerror(
                            "SQL Error",
                            f"Error inserting field result for rule {rule_id}, record {record_id}:\n{e}"
                        )

                    # Dodajemy do listy rekordów do CSV
                    record_for_csv = {
                        'rule_id': rule_id,
                        'record_id': record_id,
                        'checked_field': checked_field_name,
                        'field_value': field_value,
                        'test_result': test_result,
                        'error_message': message
                    }
                    all_records_for_csv.append(record_for_csv)

                conn.commit()
                rules_executed += 1
                results_summary.append(f"Rule {rule_id}: Passed {passed_count}, Failed {failed_count}")

            # Podsumowanie
            overall_status = "SUCCESS" if all("Passed" in r for r in results_summary) else "CHECK FAILED"
            messagebox.showinfo(
                "DQ Check Summary",
                f"Rules executed: {rules_executed}/{total_rules}\n"
                f"Total rows in CSV: {len(all_records_for_csv)}\n\n" +
                "\n".join(results_summary) +
                f"\n\nOverall Status: {overall_status}"
            )

            # Tworzenie CSV dla wszystkich reguł

            if all_records_for_csv:
                csv_file = "all_dq_rules_result.csv"
                fieldnames = ['rule_id', 'record_id', 'checked_field', 'field_value', 'test_result', 'error_message']

                try:
                    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for record in all_records_for_csv:
                            writer.writerow(record)
                    messagebox.showinfo("Export Complete",
                                        f"All rules - {len(all_records_for_csv)} records exported to CSV.")
                except Exception as e:
                    messagebox.showerror("CSV Error", f"Error exporting CSV:\n{e}")

            # if all_records_for_csv:
            #     all_keys = set()
            #     for rec in all_records_for_csv:
            #         all_keys.update(rec.keys())
            #     fieldnames = list(all_keys)
            #
            #     csv_file = f"all_dq_rules_result.csv"
            #     try:
            #         with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            #             writer = csv.DictWriter(f, fieldnames=fieldnames)
            #             writer.writeheader()
            #             for record in all_records_for_csv:
            #                 writer.writerow(record)
            #         messagebox.showinfo("Export Complete",
            #                             f"All rules - {len(all_records_for_csv)} records exported to CSV.")
            #     except Exception as e:
            #         messagebox.showerror("CSV Error", f"Error exporting CSV:\n{e}")

        finally:
            cursor.close()
            conn.close()

    def run_selected_dq_rule(self, table, rule_id):
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT sql_query, version, target_table, error_message FROM dq_rules WHERE id=%s AND status='ACTIVE'",
                (rule_id,)
            )
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Error", f"Rule {rule_id} not found or inactive.")
                return

            sql_query = row['sql_query']
            rule_version = row['version']
            rule_error_message = row.get('error_message') or "DQ check failed"

            # Wykonanie zapytania SQL reguły
            try:
                cursor.execute(sql_query)
                records = cursor.fetchall()
            except mysql.connector.Error as e:
                messagebox.showerror("SQL Error", f"Error executing rule {rule_id}:\n{e}")
                return

            if not records:
                messagebox.showinfo("Info", f"Rule {rule_id} returned no records.")
                return

            failed_count = sum(1 for r in records if r.get('dq_check', 1) == 0)
            passed_count = sum(1 for r in records if r.get('dq_check', 1) == 1)

            # WSTAWIENIE DO dq_results
            try:
                cursor.execute(
                    """
                    INSERT INTO dq_results
                    (rule_id, rule_version, failed_count, passed_count)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (rule_id, rule_version, failed_count, passed_count)
                )
            except mysql.connector.Error as e:
                messagebox.showerror("SQL Error", f"Error inserting DQ results for rule {rule_id}:\n{e}")

            #WSTAWIENIE DO dq_field_results
            for record in records:
                record_id = str(record.get('id', 'unknown'))
                test_result = record.get('dq_check', 1)
                message = "DQ check passed" if test_result == 1 else rule_error_message

                #Wybieram tylko drugą kolumnę SELECTa
                checked_field = list(record.keys())[1]
                field_value = record.get(checked_field, "")

                try:
                    cursor.execute(
                        """
                        INSERT INTO dq_field_results
                        (rule_id, rule_version, record_id, field_name, field_value, test_result, error_message, target_table)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            rule_id,
                            rule_version,
                            record_id,
                            checked_field,
                            str(field_value) if field_value is not None else "",
                            test_result,
                            message,
                            table
                        )
                    )
                except mysql.connector.Error as e:
                    messagebox.showerror(
                        "SQL Error",
                        f"Error inserting field result for rule {rule_id}, record {record_id}:\n{e}"
                    )

            conn.commit()
            messagebox.showinfo("DQ Result",
                                f"Rule {rule_id} executed.\nPassed: {passed_count}, Failed: {failed_count}")

            #CSV generate function
            for record in records:
                test_result = record.get('dq_check', 1)
                record['error_message'] = "DQ check passed" if test_result == 1 else rule_error_message

            # Tworzenie CSV
            csv_file = f"dq_rule_{rule_id}_results.csv"
            fieldnames = list(records[0].keys())  # już zawiera error_message
            try:
                with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in records:
                        writer.writerow(record)
                messagebox.showinfo("Export Complete", f"Rule {rule_id} - {len(records)} records exported to CSV.")
            except Exception as e:
                messagebox.showerror("CSV Error", f"Error exporting rule {rule_id} to CSV:\n{e}")


        finally:
            cursor.close()
            conn.close()

    # def export_dq_results_to_csv(self, records, rule_id, rule_error_message="DQ check failed"):
    #     if not records:
    #         return
    #
    #     csv_file = f"dq_rule_{rule_id}_results.csv"
    #     fieldnames = list(records[0].keys()) + ['test_result', 'error_message']
    #
    #     try:
    #         with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    #             writer = csv.DictWriter(f, fieldnames=fieldnames)
    #             writer.writeheader()
    #             for record in records:
    #                 record_copy = record.copy()
    #                 test_result = record.get('dq_check', 1)
    #                 record_copy['test_result'] = test_result
    #                 # Użycie przekazanego error message
    #                 record_copy['error_message'] = "DQ check passed" if test_result == 1 else rule_error_message
    #                 writer.writerow(record_copy)
    #
    #         messagebox.showinfo("Export Complete", f"Rule {rule_id} - {len(records)} records exported to CSV.")
    #     except Exception as e:
    #         messagebox.showerror("CSV Error", f"Error exporting rule {rule_id} to CSV:\n{e}")

    # def run_active_dq_rules_and_export_csv(self, output_dir="dq_errors_csv"):
    #     os.makedirs(output_dir, exist_ok=True)

    #
    #             # Zapis CSV wszystkich rekordów z dodatkową kolumną komunikatów
    #             if records:
    #                 csv_file = os.path.join(output_dir, f"rule_{rule_id}_field_results.csv")
    #                 try:
    #                     with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    #                         fieldnames = list(records[0].keys()) + ['test_result', 'error_message']
    #                         writer = csv.DictWriter(f, fieldnames=fieldnames)
    #                         writer.writeheader()
    #                         for record in records:
    #                             test_result = record.get('dq_check', 1)
    #                             record_copy = record.copy()
    #                             record_copy['test_result'] = test_result
    #                             record_copy[
    #                                 'error_message'] = rule_error_message if test_result == 0 else "DQ check passed"
    #                             writer.writerow(record_copy)
    #                     messagebox.showinfo("Export Complete",
    #                                         f"Rule {rule_id} - {len(records)} records exported to CSV and DB.")
    #                 except Exception as e:
    #                     messagebox.showerror("CSV Error", f"Error exporting rule {rule_id} to CSV:\n{e}")
    #
    #         conn.commit()
    #         messagebox.showinfo("DQ Check Complete", "All active DQ rules executed and field results exported.")


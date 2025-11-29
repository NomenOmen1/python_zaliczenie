import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import config
import time
import json
from check_dq_panel import CheckDqPanel

class DataQualityWindow:
    def __init__(self, root, username, role, dashboard_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.dashboard_root = dashboard_root
        self.time_var = time_var

        self.root.title("Data Quality Panel")
        self.root.geometry("1600x800")

        tk.Label(root, text=f"Logged in as: {username}", anchor="e").pack(fill="x", padx=10, pady=5)

        # Zegar
        self.clock_label = tk.Label(root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        tk.Button(root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

        # TOP FRAME - przyciski
        top_frame = tk.Frame(self.root)
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        #left frame
        left_frame = tk.Frame(top_frame)
        left_frame.pack(side="left", anchor="w", padx=10, pady=5)
        tk.Button(left_frame, text="Add Rule", command=self.add_rule_window).pack(side="left", padx=5)
        tk.Button(left_frame, text="Deactivate Rule", command=self.deactivate_dq_rule).pack(side="left", padx=5)

        #right frame
        right_frame = tk.Frame(top_frame)
        right_frame.pack(side="right", padx=10, pady=5)
        tk.Button(right_frame, text="Check DQ", command=self.check_dq_panel).pack(side="right", padx=15, pady=10)


        # TREEVIEW LIVE RULES
        tk.Label(root, text="Live Rules", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        self.tree_frame = tk.Frame(root)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree_scroll_y = tk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree_scroll_x = tk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("id", "status", "created_at", "activated_at", "version", "description", "rule_type", "sql_query"),
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set,
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        live_column_widths = {
            "id": 20,
            "status": 40,
            "created_at": 60,
            "activated_at": 60,
            "version": 20,
            "description": 160,
            "rule_type": 30,
            "sql_query": 40,
        }

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=live_column_widths[col], anchor=tk.CENTER)

        self.load_rules()

        middle_frame = tk.Frame(self.root)
        middle_frame.pack(fill="x", padx=10, pady=(20,5))
        tk.Button(middle_frame, text="Modify Rule", command=self.modify_dq_rule).pack(side="left", padx=5)

        # TREEVIEW ARCHIVED RULES
        tk.Label(root, text="Archived Rules", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        self.archive_frame = tk.Frame(root)
        self.archive_frame.pack(fill="both", expand=True)

        self.archive_scroll_y = tk.Scrollbar(self.archive_frame, orient="vertical")
        self.archive_scroll_y.pack(side="right", fill="y")
        self.archive_scroll_x = tk.Scrollbar(self.archive_frame, orient="horizontal")
        self.archive_scroll_x.pack(side="bottom", fill="x")

        self.archive_tree = ttk.Treeview(
            self.archive_frame,
            columns=("history_id", "rule_id", "version", "status", "created_at", "description", "rule_type", "rule_params", "deactivated_by", "deactivated_at"),
            yscrollcommand=self.archive_scroll_y.set,
            xscrollcommand=self.archive_scroll_x.set,
            show="headings"
        )
        self.archive_tree.pack(fill="both", expand=True)
        self.archive_scroll_y.config(command=self.archive_tree.yview)
        self.archive_scroll_x.config(command=self.archive_tree.xview)

        archive_column_widths = {
            "history_id": 20,
            "rule_id": 20,
            "version": 20,
            "status": 50,
            "created_at": 60,
            "description": 160,
            "rule_type": 50,
            "rule_params": 160,
            "deactivated_by": 40,
            "deactivated_at": 60,
        }

        for col in self.archive_tree["columns"]:
            self.archive_tree.heading(col, text=col)
            self.archive_tree.column(col, width=archive_column_widths[col], anchor=tk.CENTER)

        self.load_archive_rules()

    def go_back(self):
        self.root.destroy()
        self.dashboard_root.deiconify()

    def load_rules(self):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, created_at, activated_at, version, description, rule_type, sql_query FROM dq_rules WHERE status = 'active'")
            rows = cursor.fetchall()

            for row in rows:
                self.tree.insert("", "end", values=row)

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

#####################################################
    def add_rule_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add new DQ Rule")

        tk.Label(win, text="Description:").pack()
        desc_entry = tk.Entry(win, width=50)
        desc_entry.pack()

        tk.Label(win, text="Rule Type:").pack()
        type_entry = tk.Entry(win)
        type_entry.pack()

        tk.Label(win, text="SQL Query:").pack()
        sql_entry = tk.Text(win, height=5, width=60)
        sql_entry.pack()

        def submit():
            desc = desc_entry.get()
            rule_type = type_entry.get()
            sql_query = sql_entry.get("1.0", "end-1c")

            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO dq_rules (description, rule_type, sql_query, version) VALUES (%s, %s, %s, %s)",
                (desc, rule_type, sql_query, "1.0")
            )
            conn.commit()
            cursor.close()
            conn.close()

            self.tree.delete(*self.tree.get_children())  # odśwież drzewo
            self.load_rules()
            win.destroy()

        tk.Button(win, text="Add new DQ Rule", command=submit).pack(pady=10)

    def deactivate_dq_rule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No rule was selected")
            return

        rule_id = self.tree.item(selected[0], "values")[0]

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        try:
            # Pobierz aktywnego rula
            cursor.execute("""
                SELECT id, status, version, description, rule_type, sql_query, created_at
                FROM dq_rules
                WHERE id=%s AND status='ACTIVE'
            """, (rule_id,))
            row = cursor.fetchone()

            if not row:
                messagebox.showinfo("Info", "This rule is already inactive")
                return

            rid, status, version, desc, rule_type, sql_query, created_at = row

            # --- wersja do archiwizacji ---
            archived_version = version if version else "1.0"

            # --- JSON rule_params ---
            import json
            rule_params_json = json.dumps({
                "sql_query": sql_query,
                "description": desc
            })

            # --- Archiwizacja ---
            cursor.execute("""
                INSERT INTO dq_rules_history
                (rule_id, version, status, created_at, description, rule_type, rule_params,
                 deactivated_by, deactivated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s,
                        %s, NOW())
            """, (
                rid, archived_version, "INACTIVE",
                created_at,
                desc,
                rule_type,
                rule_params_json,
                self.username
            ))

            # --- Update rula ---
            cursor.execute("""
                UPDATE dq_rules
                SET status='INACTIVE'
                WHERE id=%s
            """, (rid,))

            conn.commit()

            messagebox.showinfo("Info", "Rule has been deactivated and archived")

        except mysql.connector.Error as e:
            messagebox.showerror("DB Error", str(e))

        finally:
            cursor.close()
            conn.close()

            # Odśwież oba drzewa
            self.tree.delete(*self.tree.get_children())
            self.load_rules()

            self.archive_tree.delete(*self.archive_tree.get_children())
            self.load_archive_rules()

    def modify_dq_rule(self):
        selected = self.archive_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select Rule from Archived Rules")
            return

        # Pierwsza kolumna to history_id
        history_id = self.archive_tree.item(selected[0], "values")[0]

        # Pobierz dane z ARCHIWUM
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rule_id, description, rule_type, rule_params, version
            FROM dq_rules_history
            WHERE history_id=%s
        """, (history_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Rule not found in database")
            return

        rule_id, current_desc, current_type, rule_params_json, archived_version = row

        # rule_params to JSON -> pobieramy SQL
        params = json.loads(rule_params_json)
        current_sql = params.get("sql_query", "")

        # ---- OKNO MODYFIKACJI ----
        win = tk.Toplevel(self.root)
        win.title("Modify DQ Rule")

        tk.Label(win, text="Description:").pack()
        desc_entry = tk.Entry(win, width=50)
        desc_entry.insert(0, current_desc)
        desc_entry.pack()

        tk.Label(win, text="Rule Type:").pack()
        type_entry = tk.Entry(win)
        type_entry.insert(0, current_type)
        type_entry.pack()

        tk.Label(win, text="SQL Query:").pack()
        sql_entry = tk.Text(win, height=5, width=60)
        sql_entry.insert("1.0", current_sql)
        sql_entry.pack()

        def save_changes():
            new_desc = desc_entry.get()
            new_type = type_entry.get()
            new_sql = sql_entry.get("1.0", "end-1c")

            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()

            cursor.execute("""
                    SELECT COUNT(*) 
                    FROM dq_rules 
                    WHERE id=%s AND status='ACTIVE'
                """, (rule_id,))
            active_count = cursor.fetchone()[0]

            if active_count > 0:
                messagebox.showerror("Error", f"Rule {rule_id} is already active and cannot be modified from archive.")
                cursor.close()
                conn.close()
                return

            # --- inkrementacja wersji przy restore ---
            major, minor = archived_version.split(".")
            minor = int(minor) + 1
            new_version = f"{major}.{minor}"

            # Aktualizacja live rula
            cursor.execute("""
                UPDATE dq_rules
                SET description=%s,
                    rule_type=%s,
                    sql_query=%s,
                    status='ACTIVE',
                    version=%s,
                    activated_at=NOW()
                WHERE id=%s
            """, (new_desc, new_type, new_sql, new_version, rule_id))

            cursor.execute("""
                UPDATE dq_rules
                SET description=%s,
                    rule_type=%s,
                    sql_query=%s,
                    status='ACTIVE'
                WHERE id=%s
            """, (new_desc, new_type, new_sql, rule_id))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Info", "Rule has been updated")

            self.tree.delete(*self.tree.get_children())
            self.load_rules()

            win.destroy()

        tk.Button(win, text="Save changes", command=save_changes).pack(pady=10)

    def load_archive_rules(self):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM dq_rules_history
            """)
            rows = cursor.fetchall()

            for row in rows:
                self.archive_tree.insert("", "end", values=row)

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def check_dq_panel(self):
        self.root.withdraw()
        new_window = tk.Toplevel(self.root)
        CheckDqPanel(new_window, self.username, self.role, self.root, self.time_var)





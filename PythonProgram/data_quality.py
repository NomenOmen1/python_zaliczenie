import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import config
import time

class DataQualityWindow:
    def __init__(self, root, username, role, dashboard_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.dashboard_root = dashboard_root
        self.time_var = time_var

        self.root.title("Data Quality Panel")
        self.root.geometry("2000x600")

        tk.Label(root, text=f"Logged in as: {username}", anchor="e").pack(fill="x", padx=10, pady=5)

        # Zegar
        self.clock_label = tk.Label(root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        tk.Button(root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

        #Definiowanie TOP FRAME
        top_frame = tk.Frame(self.root)
        top_frame.pack(side="top", anchor="w", padx=10, pady=5)

        # Add Rule
        addRuleButton = tk.Button(top_frame, text="Add Rule", command=self.add_rule_window)
        addRuleButton.pack(side="left", padx=5)

        # Deactivate Rule
        deactivateRuleButton = tk.Button(top_frame, text="Deactivate Rule", command=self.deactivate_dq_rule)
        deactivateRuleButton.pack(side="left", padx=5)

        #Modify Rule
        modifyRuleButton = tk.Button(top_frame, text = 'Modify Rule', command=self.modify_dq_rule)
        modifyRuleButton.pack(side="left", padx=5)

        # TREEVIEW LIVE
        #tk.label(root, text="Archive Rules", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
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

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)

        self.load_rules()

        # TREEVIEW ARCHIVE



    def go_back(self):
        self.root.destroy()
        self.dashboard_root.deiconify()

    def load_rules(self):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, created_at, activated_at, version, description, rule_type, sql_query FROM dq_rules")
            rows = cursor.fetchall()

            for row in rows:
                self.tree.insert("", "end", values=row)

        except mysql.connector.Error as e:
            messagebox.showerror("Błąd", f"Błąd bazy danych: {e}")
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
                "INSERT INTO dq_rules (description, rule_type, sql_query) VALUES (%s, %s, %s)",
                (desc, rule_type, sql_query)
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
            # Dezaktywacja reguły
            cursor.execute(
                "UPDATE dq_rules SET status='INACTIVE' WHERE id=%s AND status='ACTIVE'",
                (rule_id,)
            )
            if cursor.rowcount == 0:
                messagebox.showinfo("Info", "This rule is already inactive")
                return
            else:
                conn.commit()
                messagebox.showinfo("Info", "Rule has been deactivated")

            # Archiwizacja reguły (po dezaktywacji)
            cursor.execute("""
                SELECT id, status, version, description, rule_type, sql_query
                FROM dq_rules WHERE id=%s
            """, (rule_id,))
            row = cursor.fetchone()
            if row:
                rid, status, version, desc, rule_type, sql_query = row
                cursor.execute("""
                    INSERT INTO dq_rules_history
                    (rule_id, status, version, description, rule_type, sql_query, changed_by, changed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (rid, status, version, desc, rule_type, sql_query, self.username))
                conn.commit()

            # Odświeżanie drzewa po dezaktywacji i archiwizacji
            self.tree.delete(*self.tree.get_children())
            self.load_rules()

        finally:
            cursor.close()
            conn.close()

    def modify_dq_rule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No rule was selected")
            return

        rule_id = self.tree.item(selected[0], "values")[0]

        # Pobierz istniejące dane rula
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT description, rule_type, sql_query FROM dq_rules WHERE id=%s",
            (rule_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Rule not found in database")
            return

        current_desc, current_type, current_sql = row

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
            cursor.execute(
                "UPDATE dq_rules SET description=%s, rule_type=%s, sql_query=%s, status='ACTIVE' WHERE id=%s",
                (new_desc, new_type, new_sql, rule_id)
            )
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Info", "Rule has been updated")

            self.tree.delete(*self.tree.get_children())
            self.load_rules()

            win.destroy()

        tk.Button(win, text="Save changes", command=save_changes).pack(pady=10)



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
        self.root.geometry("800x400")

        tk.Label(root, text=f"Logged in as: {username}", anchor="e").pack(fill="x", padx=10, pady=5)

        # Zegar
        self.clock_label = tk.Label(root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        tk.Button(root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

        tk.Button(root, text="Add Rule", command=self.add_rule_window).pack(pady=5)

        # TREEVIEW
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

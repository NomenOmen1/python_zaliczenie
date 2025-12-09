import re
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from login_functions import create_user, change_password, deactivate_user, get_all_users, change_user_role
from utils import place_window
from db_config import config
import mysql.connector
from mysql.connector import Error

class AdminWindow:
    def __init__(self, root, username, role, dashboard_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.dashboard_root = dashboard_root
        self.time_var = time_var

        self.root.title("Panel Admina")
        place_window(self.root, width=550, height=465)


        tk.Label(root, text=f"Logged in as: {username}", anchor="e").pack(fill="x", padx=10, pady=10)

        self.clock_label = tk.Label(root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        # tk.Button(root, text="Nowy Użytkownik", command=self.add_user).pack(pady=5)
        # tk.Button(root, text="Zmień Hasło", command=self.change_password).pack(pady=5)
        # tk.Button(root, text="Deactivate User", command=self.deactivate_user).pack(pady=5)

        # frame = tk.Frame(self.root)
        # frame.pack(padx=10, pady=10, fill="x")
        #
        # button1 = tk.Button(frame, text="New User", command=self.add_user)
        # button2 = tk.Button(frame, text="Change Password", command=self.change_password)
        # button3 = tk.Button(frame, text="Deactivate User", command=self.deactivate_user)
        # button4 = tk.Button(frame, text="Change Role", command=self.change_role)
        #
        # button1.grid(row=0, column=0, sticky="nsew")
        # button2.grid(row=0, column=1, sticky="nsew")
        # button3.grid(row=0, column=2, sticky="nsew")
        # button4.grid(row=0, column=3, sticky="nsew")
        #
        # frame.grid_columnconfigure(0, weight=1)
        # frame.grid_columnconfigure(1, weight=1)
        # frame.grid_columnconfigure(2, weight=1)
        # frame.grid_columnconfigure(3, weight=1)
        #
        # # USER LIST
        # tk.Label(root, text="User List", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        # self.user_frame = tk.Frame(frame)
        # self.user_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        #
        # # Scrollbary
        # self.user_tree_scroll_y = tk.Scrollbar(self.user_frame, orient="vertical")
        # self.user_tree_scroll_y.pack(side="right", fill="y")
        #
        # self.user_tree_scroll_x = tk.Scrollbar(self.user_frame, orient="horizontal")
        # self.user_tree_scroll_x.pack(side="bottom", fill="x")
        #
        # # Treeview
        # self.user_tree = ttk.Treeview(
        #     self.user_frame,
        #     columns=("id", "username", "created_at", "role", "active"),
        #     yscrollcommand=self.user_tree_scroll_y.set,
        #     xscrollcommand=self.user_tree_scroll_x.set,
        #     show="headings"
        # )
        # self.user_tree.pack(fill="both", expand=True)
        #
        # # Podłącz scrollbary
        # self.user_tree_scroll_y.config(command=self.user_tree.yview)
        # self.user_tree_scroll_x.config(command=self.user_tree.xview)
        #
        # # Nagłówki kolumn
        # for col in ("id", "username", "created_at", "role", "active"):
        #     self.user_tree.heading(col, text=col.title())
        #     self.user_tree.column(col, width=100, anchor="center")

        # --- FRAME NA PRZYCISKI ---
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        buttons = [
            ("New User", self.add_user),
            ("Change Password", self.change_password),
            ("Deactivate User", self.deactivate_user),
            ("Change Role", self.change_role)
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=5)
            button_frame.grid_columnconfigure(i, weight=1)

        # --- LABEL ---
        tk.Label(self.root, text="User List", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))

        # --- FRAME NA TREEVIEW ---
        self.user_frame = tk.Frame(self.root)
        self.user_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollbary
        self.user_tree_scroll_y = tk.Scrollbar(self.user_frame, orient="vertical")
        self.user_tree_scroll_y.pack(side="right", fill="y")
        self.user_tree_scroll_x = tk.Scrollbar(self.user_frame, orient="horizontal")
        self.user_tree_scroll_x.pack(side="bottom", fill="x")

        # Treeview
        self.user_tree = ttk.Treeview(
            self.user_frame,
            columns=("id",
                     "username",
                     #"created_at",
                     "role",
                     "active"),
            show="headings",
            yscrollcommand=self.user_tree_scroll_y.set,
            xscrollcommand=self.user_tree_scroll_x.set
        )
        self.user_tree.pack(fill="both", expand=True)

        # Podłącz scrollbary
        self.user_tree_scroll_y.config(command=self.user_tree.yview)
        self.user_tree_scroll_x.config(command=self.user_tree.xview)

        users_column_width = {
            "id": 10,
            "username": 30,
            #"created_at": 50,
            "role": 30,
            "active": 30,
        }

        # Nagłówki kolumn
        for col in ("id", "username", "role", "active"):
            self.user_tree.heading(col, text=col.title())
            self.user_tree.column(col, width=users_column_width[col], anchor="center")


        self.get_users_overview()

        # POWRÓT
        tk.Button(root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=15)
        self.root.protocol("WM_DELETE_WINDOW", self.go_back)  # wciśnięcie X w prawym górnym rogu działa jak BACK

    def go_back(self):
        self.root.destroy()               # zamykanie panelu admina
        self.dashboard_root.deiconify()   # przywracanie dashboardu

    def add_user(self):
        win = tk.Toplevel(self.root)
        win.title("Add a new user")
        self.place_smaller_window(win)

        tk.Label(win, text="Username:").pack()
        username_entry = tk.Entry(win)
        username_entry.pack()

        tk.Label(win, text="Password:").pack()
        password_entry = tk.Entry(win, show="*")
        password_entry.pack()
        tk.Label(win, text="At least 6 characters long\n1 number and 1 uppercase", fg="red").pack(padx=(1,1))

        def submit():
            user = username_entry.get()
            password = password_entry.get()

            password_pattern = r'^(?=.*[A-Z])(?=.*\d).{6,}$'

            if not re.match(password_pattern, password):
                messagebox.showerror("Error", "Password must contain at least 1 number, 1 uppercase letter and be at least 6 characters long")
                return

            try:
                create_user(user, password, role="user")
                messagebox.showinfo("Success", f"The user {user} has been created!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        tk.Button(win, text="Dodaj", command=submit).pack(pady=10)

    def change_password(self):
        users = get_all_users()

        win = tk.Toplevel(self.root)
        win.title("Change Password")
        self.place_smaller_window(win)

        tk.Label(win, text="Choose User:").pack(pady=5)
        selected_user = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=selected_user, values=users, state="readonly")
        combo.pack(pady=5)
        if users:
            combo.current(0)

        tk.Label(win, text="New Password: ").pack(pady=5)
        new_password_entry = tk.Entry(win, show="*")
        new_password_entry.pack(pady=5)
        tk.Label(win, text="At least 6 characters long\n1 number and 1 uppercase", fg="red").pack(padx=(1, 1))

        def submit():
            user = selected_user.get()
            new_password = new_password_entry.get()

            password_pattern = r'^(?=.*[A-Z])(?=.*\d).{6,}$'

            if not re.match(password_pattern, new_password):
                messagebox.showerror("Error",
                                     "Password must contain at least 1 number, 1 uppercase letter and be at least 6 characters long")
                return
            try:
                change_password(user, new_password)
                messagebox.showinfo("Success", f"Password for {user} has been changed successfully.\nAccount status: active")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        tk.Button(win, text="Change Password", command=submit).pack(pady=10)

    def deactivate_user(self):
        users = get_all_users()

        win = tk.Toplevel(self.root)
        win.title("Deactivate User")
        self.place_smaller_window(win)

        tk.Label(win, text="Choose user:", anchor="e").pack(pady=5)
        selected_user = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=selected_user, values=users, state="readonly")
        combo.pack(pady=5)
        if users:
            combo.current(0)

        def submit():
            user = selected_user.get()
            try:
                deactivate_user(user)
                messagebox.showinfo("Success!", f"The user {user} has been deactivated!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Deactivate User", command=submit).pack(pady=5)

    def place_smaller_window(self, window, width=250, height=200):

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 3

        window.geometry(f"{width}x{height}+{x}+{y}")

    def change_role(self):
        win = tk.Toplevel(self.root)
        win.title("Change Role")
        self.place_smaller_window(win)

        users = get_all_users()
        roles = ('admin','user')

        tk.Label(win, text="Choose user:").pack(pady=5)
        selected_user = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=selected_user, values=users, state="readonly")
        combo.pack(pady=5)
        if users:
            combo.current(0)

        user_dropdown = ttk.Combobox(win, values=roles, state="readonly")
        user_dropdown.set("Select new role")
        user_dropdown.pack(pady=5)

        def submit():
            user = selected_user.get()
            new_role = user_dropdown.get()
            if new_role == 'admin':
                result = messagebox.askyesno("Admin", "Admin role selected, are you sure?")
                if not result:
                    messagebox.showerror("Info", "The operation was cancelled")
                    return
            try:
                change_user_role(user, new_role)
                messagebox.showinfo("Success", f"The user {user} has been assigned with a role {new_role}.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Update role", command=submit).pack(pady=10)

    def get_users_overview(self):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role, CASE WHEN active = 1 THEN 'Active' ELSE 'Inactive' END as active FROM users"
            )
            rows = cursor.fetchall()

            # Czyszczenie starych danych
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)

            for row in rows:
                self.user_tree.insert("", "end", values=row)

        except Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()









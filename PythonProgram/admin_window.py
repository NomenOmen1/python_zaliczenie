from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from login_functions import create_user, change_password, deactivate_user, get_all_users
from utils import place_window

class AdminWindow:
    def __init__(self, root, username, role, dashboard_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.dashboard_root = dashboard_root
        self.time_var = time_var

        # self.window_width = 400
        # self.window_height = 300
        self.root.title("Panel Admina")
        place_window(self.root, width=400, height=300)
        # self.root.geometry(f"{self.window_width}x{self.window_height}")

        tk.Label(root, text=f"Logged in as: {username}", anchor="e").pack(fill="x", padx=10, pady=10)

        self.clock_label = tk.Label(root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        # tk.Button(root, text="Nowy Użytkownik", command=self.add_user).pack(pady=5)
        # tk.Button(root, text="Zmień Hasło", command=self.change_password).pack(pady=5)
        # tk.Button(root, text="Deactivate User", command=self.deactivate_user).pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="x")

        button1 = tk.Button(frame, text="Nowy Użytkownik", command=self.add_user)
        button2 = tk.Button(frame, text="Zmień Hasło", command=self.change_password)
        button3 = tk.Button(frame, text="Deactivate User", command=self.deactivate_user)

        button1.grid(row=0, column=0, sticky="nsew")
        button2.grid(row=0, column=1, sticky="nsew")
        button3.grid(row=0, column=2, sticky="nsew")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        # POWRÓT
        tk.Button(root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=15)
        self.root.protocol("WM_DELETE_WINDOW", self.go_back)  # wciśnięcie X w prawym górnym rogu działa jak BACK

    def go_back(self):
        self.root.destroy()               # zamykanie panelu admina
        self.dashboard_root.deiconify()   # przywracanie dashboardu

    def add_user(self):
        win = tk.Toplevel(self.root)
        win.title("Add a new user")

        tk.Label(win, text="Username:").pack()
        username_entry = tk.Entry(win)
        username_entry.pack()

        tk.Label(win, text="Password:").pack()
        password_entry = tk.Entry(win, show="*")
        password_entry.pack()

        def submit():
            user = username_entry.get()
            password = password_entry.get()
            try:
                create_user(user, password, role="user")
                messagebox.showinfo("Sukces", f"Użytkownik {user} został utworzony!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        tk.Button(win, text="Dodaj", command=submit).pack(pady=10)

    def change_password(self):
        users = get_all_users()

        win = tk.Toplevel(self.root)
        win.title("Change Password")

        tk.Label(win, text="Wybierz Użytkownika:").pack(pady=5)
        selected_user = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=selected_user, values=users, state="readonly")
        combo.pack(pady=5)
        if users:
            combo.current(0)

        tk.Label(win, text="Nowe hasło: ").pack(pady=5)
        new_password_entry = tk.Entry(win, show="*")
        new_password_entry.pack(pady=5)

        def submit():
            user = selected_user.get()
            new_password = new_password_entry.get()
            try:
                change_password(user, new_password)
                messagebox.showinfo("Success", f"Password for {user} has been changed successfully. \nAccount status: active")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        tk.Button(win, text="Zmień hasło", command=submit).pack(pady=10)

    def deactivate_user(self):
        users = get_all_users()

        win = tk.Toplevel(self.root)
        win.title("Deactivate User")

        tk.Label(win, text="Wybierz Użytkownika:", anchor="e").pack(pady=5)
        selected_user = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=selected_user, values=users, state="readonly")
        combo.pack(pady=5)
        if users:
            combo.current(0)

        def submit():
            user = selected_user.get()
            try:
                deactivate_user(user)
                messagebox.showinfo("Sukces!", f"The user {user} has been deactivated!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Deactivate User", command=submit).pack(pady=5)



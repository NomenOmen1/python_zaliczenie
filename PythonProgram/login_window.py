import tkinter as tk
from tkinter import messagebox
from login_functions import login_user
from dashboard_window import DashboardWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login panel")
        self.root.geometry("400x300")

        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.validate_login).pack(pady=10)

    def validate_login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        logged_user, role, error = login_user(user, pwd)

        if error:
            messagebox.showerror("Login Failed", error)
            return

        messagebox.showinfo("Success", f"Logged in as: {logged_user}")

        # Usunięcie okna logowania
        for widget in self.root.winfo_children():
            widget.destroy()

        # Przejście do głównego okna
        DashboardWindow(self.root, logged_user, role)

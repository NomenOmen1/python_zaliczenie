import tkinter as tk
from tkinter import messagebox
from login_functions import login_user
from dashboard_window import DashboardWindow
from utils import place_window

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login panel")
        self.root.geometry("400x300")
        #place_window(self.root)

        tk.Label(root, text="Username:").pack(pady=(30,0))
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.validate_login).pack(pady=10)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side="bottom", fill="x")

        # EXIT pozycja
        tk.Button(bottom_frame, text="EXIT", command=self.exit_program_login).pack(side="left", padx=10, pady=5)

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

    def exit_program_login(self):
        self.root.destroy()

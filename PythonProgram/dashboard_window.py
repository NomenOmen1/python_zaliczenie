import tkinter as tk
from admin_window import AdminWindow
import time

class DashboardWindow:
    def __init__(self, root, username, role):
        self.root = root
        self.username = username
        self.role = role

        self.window_width = 400
        self.window_height = 300
        self.root.title("Panel główny")
        self.root.geometry(f"{self.window_width}x{self.window_height}")


        # Pasek użytkownika
        tk.Label(root,text=f"ZALOGOWANO JAKO: {username}",anchor="e").pack(fill="x", padx=10, pady=10)

        # Przycisk Panel Admina tylko dla admina
        if role == "admin":
            tk.Button(root, text="Panel Admina", command=self.open_admin_panel).pack(pady=5)

        # Przykładowe funkcje
        tk.Button(root, text="Opcja 1").pack(pady=5)
        tk.Button(root, text="Opcja 2").pack(side = "left", pady=5)

        # ZEGAR

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side = "bottom", fill="x")

        self.time_var = tk.StringVar()
        # self.clock_frame = tk.Frame(root)
        # self.clock_frame.pack(side="bottom", fill="x")
        self.clock_label = tk.Label(bottom_frame, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="right", anchor = "se", padx=10, pady=5)

        self.update_time()

    def update_time(self):
        current_time = time.strftime('%H:%M:%S')
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)

    def open_admin_panel(self):
        # Ukrywamy dashboard
        self.root.withdraw()

        # Tworzymy nowe okno admina
        admin_window = tk.Toplevel()
        admin_app = AdminWindow(admin_window, self.username, self.role, self.root, self.time_var)

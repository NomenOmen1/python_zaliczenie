import tkinter as tk
from admin_window import AdminWindow

class DashboardWindow:
    def __init__(self, root, username, role):
        self.root = root
        self.username = username
        self.role = role

        root.title("Panel główny")

        # Pasek użytkownika
        tk.Label(
            root,
            text=f"ZALOGOWANO JAKO: {username}",
            anchor="e"
        ).pack(fill="x", padx=10, pady=10)

        # Przycisk Panel Admina tylko dla admina
        if role == "admin":
            tk.Button(root, text="Panel Admina", command=self.open_admin_panel).pack(pady=5)

        # Przykładowe funkcje
        tk.Button(root, text="Opcja 1").pack(pady=5)
        tk.Button(root, text="Opcja 2").pack(pady=5)

    def open_admin_panel(self):
        # Ukrywamy dashboard
        self.root.withdraw()

        # Tworzymy nowe okno admina
        admin_window = tk.Toplevel()
        admin_app = AdminWindow(admin_window, self.username, self.role, self.root)

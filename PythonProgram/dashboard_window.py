import tkinter as tk
from tkinter import messagebox, filedialog
from admin_window import AdminWindow
import time
from csv_upload import load_csv_and_log
from data_quality import DataQualityWindow


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
        tk.Label(root,text=f"Logged in as: {username}",anchor="e").pack(fill="x", padx=10, pady=10)

        # Panel Admina tylko dla admina
        if role == "admin":
            tk.Button(root, text="Panel Admina", command=self.open_admin_panel).pack(pady=5)

        #BUTTONS
        tk.Button(root, text="Upload CSV", command=self.load_csv_and_log).pack(pady=5)

        tk.Button(root, text="Data Quality", command=self.open_dq_panel).pack(pady=5)

        # ZEGAR + EXIT (Frame bottom)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side = "bottom", fill="x")

        # EXIT pozycja
        tk.Button(bottom_frame, text="EXIT", command=self.exit_programm).pack(side="left", padx=10, pady=5)
        #ZEGAR pozycja
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

    def exit_programm(self):
        self.root.destroy()

    def load_csv_and_log(self):
        file_path = filedialog.askopenfilename(
            title="Choose CSV file",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if file_path:
            log = load_csv_and_log("data_input.csv", "customers", self.username)
            messagebox.showinfo("CSV Uploaded", log)
        if not file_path:
            messagebox.showerror("Error", "No file selected")

    def open_dq_panel(self):
        self.root.withdraw()
        dq_panel = tk.Toplevel()
        dq_app = DataQualityWindow(dq_panel, self.username, self.role, self.root, self.time_var)





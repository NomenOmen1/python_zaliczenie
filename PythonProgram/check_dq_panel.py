import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from db_config import config
import time
import json

import tkinter as tk

class CheckDqPanel:
    def __init__(self, root, username, role, data_quality_root, time_var):
        self.root = root
        self.username = username
        self.role = role
        self.data_quality_root = data_quality_root
        self.time_var = time_var

        self.root.title("DQ Panel")
        self.root.geometry("800x400")

        # Label z użytkownikiem
        tk.Label(self.root, text=f"Logged in as: {self.username}", anchor="e").pack(fill="x", padx=10, pady=5)

        # Zegar
        self.clock_label = tk.Label(self.root, textvariable=self.time_var, font=("Helvetica", 10))
        self.clock_label.pack(side="bottom", anchor="se", padx=10, pady=5)

        # Przycisk powrotu
        tk.Button(self.root, text="BACK", command=self.go_back).pack(side="bottom", anchor="sw", padx=10, pady=5)

    def go_back(self):
        self.root.destroy()
        self.data_quality_root.deiconify()


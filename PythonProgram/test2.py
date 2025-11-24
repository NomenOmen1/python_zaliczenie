import tkinter as tk
from tkinter import messagebox

# Funkcja wywoływana po kliknięciu przycisku
def on_button_click():
    messagebox.showinfo("Info", "Przycisk został kliknięty!")

# Tworzymy główne okno
root = tk.Tk()
root.title("Proste GUI w Tkinter")
root.geometry("300x150")  # szerokość x wysokość

# Dodajemy etykietę
label = tk.Label(root, text="Witaj w Tkinter!", font=("Arial", 14))
label.pack(pady=20)

# Dodajemy przycisk
button = tk.Button(root, text="Kliknij mnie", command=on_button_click)
button.pack()

# Uruchamiamy pętlę główną
root.mainloop()

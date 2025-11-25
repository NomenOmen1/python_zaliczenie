# Stwórz teraz osobne okno dostepne tylko dla ADMIN o nazwie zarzadzaj uzytkownikami, tam 3 przyciski:stworz uzytkownika, zmien haslo, dezaktywuj uzytkownika


import tkinter as tk
from tkinter import messagebox
from login_functions import login_user


# -------------------- GŁÓWNE OKNO PROGRAMU --------------------
def open_main_window(root, username, role):
    main = tk.Toplevel(root)
    main.title("Główne Okno Programu")
    main.geometry("500x300")

    # Kiedy zamkniesz główne okno → zamyka aplikację
    main.protocol("WM_DELETE_WINDOW", root.destroy)

    user_label = tk.Label(main, text=f"Zalogowano jako: {username}", font=("Arial", 10))
    user_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    welcome = tk.Label(main, text=f"Witaj, {username}!", font=("Arial", 16))
    welcome.pack(pady=20)

    role_label = tk.Label(main, text=f"Twoja rola: {role}", font=("Arial", 12))
    role_label.pack(pady=10)

    btn1 = tk.Button(main, text="Opcja 1: Panel użytkownika", width=30)
    btn1.pack(pady=10)

    btn2 = tk.Button(main, text="Opcja 2: Zarządzanie danymi", width=30)
    btn2.pack(pady=10)

    btn3 = tk.Button(main, text="Opcja 3: Ustawienia", width=30)
    btn3.pack(pady=10)


# -------------------- OKNO LOGOWANIA --------------------
def login_window():
    root = tk.Tk()
    root.title("Logowanie")
    root.geometry("400x300")

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()

        logged_user, role, error = login_user(username, password)

        if error:
            messagebox.showerror("Login Failed", error)
        else:
            messagebox.showinfo("Success", f"Zalogowano jako: {logged_user}")

            root.withdraw()  # ukrycie okna logowania
            open_main_window(root, logged_user, role)

    label = tk.Label(root, text="Witaj w Programie!", font=("Arial", 14))
    label.pack(pady=20)

    username_label = tk.Label(root, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    password_label = tk.Label(root, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(root, text="Login", command=validate_login)
    login_button.pack(pady=15)

    root.mainloop()


# ---- START PROGRAMU ----
login_window()

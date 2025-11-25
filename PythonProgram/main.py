# Stwórz teraz osobne okno dostepne tylko dla ADMIN o nazwie zarzadzaj uzytkownikami, tam 3 przyciski:stworz uzytkownika, zmien haslo, dezaktywuj uzytkownika

#Kolejny krok: stwórz panel do ładowania CSV (najlepiej wybierając plik z browse)


import tkinter as tk
from login_window import LoginWindow

def main():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

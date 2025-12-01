# Stwórz teraz osobne okno dostepne tylko dla ADMIN o nazwie zarzadzaj uzytkownikami, tam 3 przyciski:stworz uzytkownika, zmien haslo, dezaktywuj uzytkownika

#Kolejny krok: stwórz panel do ładowania CSV (najlepiej wybierając plik z browse)

# ZADANIE NA WTOREK:
# DODA DROPDOWN Z WYBOREM TABELI DLA KTÓREJ MA BYĆ pokazany WYKRES


import tkinter as tk
from login_window import LoginWindow
from utils import place_window

def main():
    root = tk.Tk()
    place_window(root)
    app = LoginWindow(root)
    #app.pack
    root.mainloop()

if __name__ == "__main__":
    main()

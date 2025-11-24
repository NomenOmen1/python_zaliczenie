while True:
    print("\n=== MENU ADMINA ===")
    print("1. Dodaj nowego użytkownika")
    print("2. Zmień hasło użytkownika")
    print("3. Dezaktywuj użytkownika")
    print("4. Wyjście")

    choice = input("Wybierz opcję: ")

    if choice == '1':
        username = input("Podaj login nowego użytkownika: ")
        password = input("Podaj hasło: ")
        new_user(username, password)
    elif choice == '2':
        username = input("Podaj login użytkownika: ")
        new_password = input("Podaj nowe hasło: ")
        change_password(username, new_password)
    elif choice == '3':
        username = input("Podaj login użytkownika do dezaktywacji: ")
        deactivate_user(username)
    elif choice == '4':
        print("Wylogowano admina.")
        break
    else:
        print("Niepoprawny wybór!")

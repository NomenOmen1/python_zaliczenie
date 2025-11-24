import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QMainWindow,
    QStackedWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from login import login_user


# ============================
#  OKNO GŁÓWNE
# ============================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.username = None
        self.role = None

        self.setFixedSize(600, 400)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_user(self, username, role):
        self.username = username
        self.role = role
        self.label.setText(f"Zalogowano jako: {username} (rola: {role})")


# ============================
#  OKNO STARTOWE
# ============================
class StartWindow(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked

        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        title = QLabel("Witaj w aplikacji!")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_start = QPushButton("Przejdź do logowania")
        btn_start.clicked.connect(self.go_to_login)

        layout.addWidget(title)
        layout.addWidget(btn_start)
        self.setLayout(layout)

    def go_to_login(self):
        self.stacked.setCurrentIndex(1)


# ============================
#  PANEL LOGOWANIA
# ============================
class LoginWindow(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked

        self.setFixedSize(400, 300)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Login")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")

        login_button = QPushButton("Zaloguj")
        login_button.clicked.connect(self.try_login)

        layout = QVBoxLayout()
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def try_login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_label.setText("Wpisz login i hasło")
            return

        user, role, error = login_user(username, password)

        if error:
            self.status_label.setText(error)
            return

        # przechodzimy do okna głównego
        main_window: MainWindow = self.stacked.widget(2)
        main_window.set_user(user, role)

        self.stacked.setCurrentIndex(2)


# ============================
#  START APLIKACJI
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    stacked = QStackedWidget()

    start_window = StartWindow(stacked)
    login_window = LoginWindow(stacked)
    main_window = MainWindow()

    stacked.addWidget(start_window)  # index 0
    stacked.addWidget(login_window)  # index 1
    stacked.addWidget(main_window)   # index 2

    stacked.setFixedSize(600, 400)
    stacked.show()

    sys.exit(app.exec())
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from login_functions import login_user


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 400)
        self.label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_user(self, username, role):
        self.label.setText(f"Zalogowano jako: {username} (rola: {role})")


class StartWindow(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        title = QLabel("Witaj w aplikacji!", alignment=Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20))
        btn_start = QPushButton("Przejdź do logowania")
        btn_start.clicked.connect(lambda: self.stacked.setCurrentIndex(1))

        layout.addWidget(title)
        layout.addWidget(btn_start)
        self.setLayout(layout)


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
        self.status_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red;")

        login_btn = QPushButton("Zaloguj")
        login_btn.clicked.connect(self.try_login)

        layout = QVBoxLayout()
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
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


        main_window: MainWindow = self.stacked.widget(2)
        main_window.set_user(user, role)
        self.stacked.setCurrentIndex(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked = QStackedWidget()

    start = StartWindow(stacked)
    login = LoginWindow(stacked)
    main = MainWindow()

    stacked.addWidget(start)
    stacked.addWidget(login)
    stacked.addWidget(main)

    stacked.setFixedSize(600, 400)
    stacked.show()
    sys.exit(app.exec())

from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox,
    QFormLayout, QStatusBar, QHeaderView
)
from models import User
from services import AuthenticationService, SessionService, ReportService


class HeaderLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 17, QFont.Weight.Bold))
        self.setObjectName("mainHeader")

    def setText(self, text):
        super().setText(str(text))


class HintLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setWordWrap(True)

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)


class UsernameInput(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Имя пользователя")
        self.setClearButtonEnabled(True)
        self.setMinimumHeight(34)

    def focusInEvent(self, event):
        self.setStyleSheet("border: 2px solid #3978c5; padding: 5px;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet("padding: 5px;")
        super().focusOutEvent(event)


class PasswordInput(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Пароль")
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setMinimumHeight(34)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.returnPressed.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class LoginButton(QPushButton):
    def __init__(self, text="Войти"):
        super().__init__(text)
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: #245fa5; color: white; padding: 7px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: #3978c5; color: white; padding: 7px;")
        super().leaveEvent(event)


class LogoutButton(QPushButton):
    def __init__(self, text="Завершить сеанс"):
        super().__init__(text)
        self.setMinimumHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDown(True)
        super().mousePressEvent(event)


class RefreshButton(QPushButton):
    def __init__(self):
        super().__init__("Обновить журнал")
        self.setMinimumHeight(34)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class SessionTable(QTableWidget):
    def __init__(self):
        super().__init__(0, 3)
        self.setHorizontalHeaderLabels(["Пользователь", "Время входа", "Время выхода"])
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.clearSelection()
            event.accept()
            return
        super().keyPressEvent(event)

    def set_sessions(self, sessions):
        self.setRowCount(0)
        for session in sorted(sessions):
            row_index = self.rowCount()
            self.insertRow(row_index)
            values = [
                session.user.display_name,
                session.format_time_in(),
                session.format_time_out(),
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self.setItem(row_index, column_index, item)


class StatusLabel(QLabel):
    def __init__(self, text="Готово"):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setWordWrap(True)

    def changeEvent(self, event):
        super().changeEvent(event)
        if self.isEnabled():
            self.setStyleSheet("color: #245a35;")
        else:
            self.setStyleSheet("color: #777777;")


class ReportPathLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setToolTip(self.text())


class AttendanceMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._current_user = None
        self._authentication_service = AuthenticationService(self._create_initial_users())
        self._session_service = SessionService()
        self._report_service = ReportService()
        self._login_time = None

        self.setWindowTitle("Система учёта посещений")
        self.setMinimumSize(850, 560)
        self._build_interface()
        self._apply_styles()
        self._refresh_table()

    @property
    def current_user(self):
        return self._current_user

    @current_user.setter
    def current_user(self, value):
        if value is not None and not isinstance(value, User):
            raise TypeError("Текущий пользователь должен быть объектом User или None.")
        self._current_user = value

    @staticmethod
    def _create_initial_users():
        # Учебные записи позволяют проверить журнал без предварительного заполнения базы.
        return [
            User("student01", "study01", "Алексей Иванов"),
            User("student02", "study02", "Мария Смирнова"),
            User("student03", "study03", "Иван Петров"),
            User("student04", "study04", "Анна Соколова"),
            User("student05", "study05", "Дмитрий Кузнецов"),
            User("student06", "study06", "Елена Попова"),
            User("student07", "study07", "Максим Васильев"),
            User("student08", "study08", "Ольга Павлова"),
            User("student09", "study09", "Никита Семёнов"),
            User("admin", "admin123", "Администратор", "Администратор"),
        ]

    def _build_interface(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(22, 18, 22, 18)
        root_layout.setSpacing(14)

        self.header_label = HeaderLabel("Система учёта посещений пользователей")
        root_layout.addWidget(self.header_label)

        self.login_group = QGroupBox("Авторизация")
        login_layout = QFormLayout(self.login_group)
        login_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        login_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.username_input = UsernameInput()
        self.password_input = PasswordInput()
        self.login_button = LoginButton()
        login_layout.addRow("Логин:", self.username_input)
        login_layout.addRow("Пароль:", self.password_input)
        login_layout.addRow("", self.login_button)
        root_layout.addWidget(self.login_group)

        action_layout = QHBoxLayout()
        self.current_user_label = HintLabel("Текущий пользователь: не выполнен вход")
        self.logout_button = LogoutButton()
        self.refresh_button = RefreshButton()
        action_layout.addWidget(self.current_user_label, 1)
        action_layout.addWidget(self.refresh_button)
        action_layout.addWidget(self.logout_button)
        root_layout.addLayout(action_layout)

        self.session_table = SessionTable()
        root_layout.addWidget(self.session_table, 1)

        self.status_label = StatusLabel("Введите учётные данные для начала работы.")
        root_layout.addWidget(self.status_label)

        self.report_path_label = ReportPathLabel(
            f"Файл отчёта при закрытии: {self._report_service.report_path}"
        )
        root_layout.addWidget(self.report_path_label)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Готово")

        self.login_button.clicked.connect(self._handle_login)
        self.password_input.returnPressed.connect(self._handle_login)
        self.logout_button.clicked.connect(self._handle_logout)
        self.refresh_button.clicked.connect(self._refresh_table)
        self.logout_button.setEnabled(False)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #f4f6f8; }
            QGroupBox { font-weight: bold; border: 1px solid #c9d1d9;
                        border-radius: 7px; margin-top: 10px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLineEdit { border: 1px solid #aeb8c2; border-radius: 4px; padding: 5px; }
            QPushButton { background: #3978c5; color: white; border: none;
                          border-radius: 4px; padding: 7px 12px; }
            QPushButton:disabled { background: #aeb8c2; color: #f4f4f4; }
            QTableWidget { background: white; border: 1px solid #d2d8de; }
            QHeaderView::section { background: #e5ebf1; padding: 7px; border: none; }
        """)
        self.login_button.setStyleSheet("background-color: #3978c5; color: white; padding: 7px;")

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_status("Заполните оба поля перед авторизацией.", error=True)
            return

        authenticated_user = self._authentication_service.authenticate(username, password)
        if authenticated_user is None:
            self._show_status("Неверный логин или пароль.", error=True)
            self.password_input.clear()
            return

        if self._current_user is not None:
            self._session_service.finish_session(self._current_user.username)

        self.current_user = authenticated_user
        self._login_time = datetime.now()
        self._session_service.start_session(authenticated_user)
        self.current_user_label.setText(
            f"Текущий пользователь: {authenticated_user.display_name} "
            f"({authenticated_user.username})"
        )
        self.logout_button.setEnabled(True)
        self.username_input.setEnabled(False)
        self.password_input.clear()
        self._show_status(f"Вход выполнен: {self._login_time.strftime('%d.%m.%Y %H:%M:%S')}")
        self._refresh_table()

    def _handle_logout(self):
        if self._current_user is None:
            self._show_status("Нет активного сеанса для завершения.", error=True)
            return

        username = self._current_user.username
        closed_session = self._session_service.finish_session(username)
        self.current_user = None
        self._login_time = None
        self.current_user_label.setText("Текущий пользователь: не выполнен вход")
        self.logout_button.setEnabled(False)
        self.username_input.setEnabled(True)
        self._show_status(f"Сеанс пользователя {username} завершён.")
        self._refresh_table()

        if closed_session is None:
            self.statusBar().showMessage("Активный сеанс не найден.", 5000)

    def _refresh_table(self):
        self.session_table.set_sessions(self._session_service.sessions)
        self.statusBar().showMessage(
            f"Записей в журнале: {len(self._session_service.sessions)}"
        )

    def _show_status(self, message, error=False):
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("color: #a12622;")
        else:
            self.status_label.setStyleSheet("color: #245a35;")
        self.statusBar().showMessage(message, 6000)

    def closeEvent(self, event):
        # Закрытие окна фиксирует выход, чтобы в отчёте не оставались открытые сеансы.
        self._session_service.close_all_active_sessions()
        success, message = self._report_service.save_report(self._session_service.sessions)
        if success:
            self.statusBar().showMessage(message)
            event.accept()
        else:
            QMessageBox.warning(self, "Ошибка сохранения отчёта", message)
            # Закрытие не блокируется: пользователь получает предупреждение,
            # а приложение не зависает из-за недоступного файла.
            event.accept()

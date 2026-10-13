from datetime import datetime
from pathlib import Path
from models import User, LoginSession, CustomMapping


class AuthenticationService:
    def __init__(self, users):
        self._users = tuple(users)
        self._users_by_username = CustomMapping()
        for user in self._users:
            self._users_by_username.set_value(user.username.casefold(), user)

    @property
    def users(self):
        return self._users

    def authenticate(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            return None
        normalized_username = username.strip().casefold()
        user = self._users_by_username.get_value(normalized_username)
        if user is None:
            return None
        if user.password != password:
            return None
        return user


class SessionService:
    def __init__(self):
        self._sessions = []
        self._active_sessions = CustomMapping()

    @property
    def sessions(self):
        return tuple(self._sessions)

    def start_session(self, user):
        if not isinstance(user, User):
            raise TypeError("Для создания сессии требуется объект User.")
        active_session = self._active_sessions.get_value(user.username.casefold())
        if active_session is not None:
            return active_session, False

        session = LoginSession(user=user, time_in=datetime.now())
        self._sessions.append(session)
        self._active_sessions.set_value(user.username.casefold(), session)
        return session, True

    def finish_session(self, username):
        if not isinstance(username, str):
            return None
        normalized_username = username.casefold()
        active_session = self._active_sessions.remove_key(normalized_username)
        if active_session is not None:
            active_session.finish(datetime.now())
        return active_session

    def close_all_active_sessions(self):
        active_usernames = list(self._active_sessions.keys)
        for username in active_usernames:
            self.finish_session(username)


class ReportService:
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, report_path="attendance_report.txt"):
        self._report_path = Path(report_path)

    @property
    def report_path(self):
        return self._report_path

    @report_path.setter
    def report_path(self, value):
        if not isinstance(value, (str, Path)):
            raise TypeError("Путь к отчёту должен быть строкой или Path.")
        self._report_path = Path(value)

    @staticmethod
    def validate_datetime(value):
        if not isinstance(value, datetime):
            raise TypeError("Для форматирования требуется объект datetime.")
        return value.strftime(ReportService.TIME_FORMAT)

    def format_session_line(self, session):
        if not isinstance(session, LoginSession):
            raise TypeError("В отчёт можно добавить только LoginSession.")
        time_in_text = self.validate_datetime(session.time_in)
        if session.time_out is None:
            time_out_text = "—"
        else:
            time_out_text = self.validate_datetime(session.time_out)
        return f"{session.user.username} | {time_in_text} | {time_out_text}"

    def build_report(self, sessions):
        lines = ["login | time_in | time_out"]
        for session in sorted(sessions):
            lines.append(self.format_session_line(session))
        return "\n".join(lines) + "\n"

    def save_report(self, sessions):
        report_text = self.build_report(sessions)
        try:
            self._report_path.write_text(report_text, encoding="utf-8")
            return True, f"Отчёт сохранён: {self._report_path.resolve()}"
        except OSError as error:
            return False, f"Не удалось сохранить отчёт: {error}"

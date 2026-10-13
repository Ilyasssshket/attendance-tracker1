from abc import ABC, abstractmethod
from datetime import datetime


class AbstractEntity(ABC):
    """Общий контракт сущностей предметной области."""

    @abstractmethod
    def get_sort_key(self):
        raise NotImplementedError


class User(AbstractEntity):
    def __init__(self, username, password, display_name, role="Пользователь"):
        self._username = username
        self._password = password
        self._display_name = display_name
        self._role = role

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Имя пользователя не может быть пустым.")
        self._username = value.strip()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if not isinstance(value, str) or len(value) < 1:
            raise ValueError("Пароль должен быть непустой строкой.")
        self._password = value

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Отображаемое имя не может быть пустым.")
        self._display_name = value.strip()

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Роль не может быть пустой.")
        self._role = value.strip()

    def get_sort_key(self):
        return self.username.casefold()

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self.username.casefold() == other.username.casefold()

    def __lt__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self.get_sort_key() < other.get_sort_key()

    def __hash__(self):
        return hash(self.username.casefold())

    def __repr__(self):
        return (
            f"User(username={self.username!r}, "
            f"display_name={self.display_name!r}, role={self.role!r})"
        )

    def __str__(self):
        return f"{self.display_name} ({self.username})"

    def __len__(self):
        return len(self.username)

    def __bool__(self):
        return bool(self.username.strip())

    def __contains__(self, text):
        if not isinstance(text, str):
            return False
        return text.casefold() in self.display_name.casefold()

    def __format__(self, format_spec):
        if format_spec == "username":
            return self.username
        if format_spec == "display":
            return self.display_name
        return str(self)


class LoginSession(AbstractEntity):
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, user, time_in=None, time_out=None):
        if not isinstance(user, User):
            raise TypeError("Сессия должна быть связана с объектом User.")
        self._user = user
        self._time_in = time_in if time_in is not None else datetime.now()
        self._time_out = time_out

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise TypeError("Поле user должно содержать объект User.")
        self._user = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        if not isinstance(value, datetime):
            raise TypeError("Время входа должно иметь тип datetime.")
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        if value is not None and not isinstance(value, datetime):
            raise TypeError("Время выхода должно иметь тип datetime или None.")
        if value is not None and value < self.time_in:
            raise ValueError("Время выхода не может быть раньше времени входа.")
        self._time_out = value

    def finish(self, timestamp=None):
        if self.time_out is None:
            chosen_timestamp = timestamp if timestamp is not None else datetime.now()
            self.time_out = chosen_timestamp

    def get_sort_key(self):
        return (self.time_in, self.user.username.casefold())

    def format_time_in(self):
        return self.time_in.strftime(self.TIME_FORMAT)

    def format_time_out(self):
        if self.time_out is None:
            return "—"
        return self.time_out.strftime(self.TIME_FORMAT)

    def __eq__(self, other):
        if not isinstance(other, LoginSession):
            return NotImplemented
        return (
            self.user == other.user
            and self.time_in == other.time_in
            and self.time_out == other.time_out
        )

    def __lt__(self, other):
        if not isinstance(other, LoginSession):
            return NotImplemented
        return self.get_sort_key() < other.get_sort_key()

    def __hash__(self):
        return hash((self.user, self.time_in, self.time_out))

    def __repr__(self):
        return (
            f"LoginSession(user={self.user.username!r}, "
            f"time_in={self.time_in!r}, time_out={self.time_out!r})"
        )

    def __str__(self):
        return f"{self.user.username}: {self.format_time_in()} — {self.format_time_out()}"

    def __len__(self):
        return 3

    def __bool__(self):
        return self.time_in is not None

    def __contains__(self, username_fragment):
        if not isinstance(username_fragment, str):
            return False
        return username_fragment.casefold() in self.user.username.casefold()


class CustomMapping:
    """Небольшой маппинг без использования dict в логике приложения."""

    def __init__(self):
        self._keys = []
        self._values = []

    @property
    def keys(self):
        return tuple(self._keys)

    @property
    def values(self):
        return tuple(self._values)

    def set_value(self, key, value):
        if key is None:
            raise ValueError("Ключ маппинга не может быть None.")
        for index, existing_key in enumerate(self._keys):
            if existing_key == key:
                self._values[index] = value
                return
        self._keys.append(key)
        self._values.append(value)

    def get_value(self, key, default=None):
        for index, existing_key in enumerate(self._keys):
            if existing_key == key:
                return self._values[index]
        return default

    def remove_key(self, key):
        for index, existing_key in enumerate(self._keys):
            if existing_key == key:
                self._keys.pop(index)
                return self._values.pop(index)
        return None

    def __contains__(self, key):
        return any(existing_key == key for existing_key in self._keys)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(tuple(self._keys))

    def __eq__(self, other):
        if not isinstance(other, CustomMapping):
            return NotImplemented
        if len(self) != len(other):
            return False
        for key in self._keys:
            if key not in other:
                return False
            if self.get_value(key) != other.get_value(key):
                return False
        return True

    def __repr__(self):
        pairs = []
        for key, value in zip(self._keys, self._values):
            pairs.append(f"{key!r}: {value!r}")
        return "CustomMapping({" + ", ".join(pairs) + "})"

    def __str__(self):
        return f"CustomMapping: {len(self)} записей"

    def __bool__(self):
        return len(self) > 0

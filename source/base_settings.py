import threading
import sys
import json


class BaseSettings:
    def __init__(self):
        self._index = 0
        self._keys = list(self.__dict__.keys())  # Store instance variable names
        self._lock = threading.Lock()  # Create a lock object

    def __iter__(self):
        with self._lock:  # Acquire the lock
            self._index = 0  # Reset the index every time iter is called
            self._keys = list(self.__dict__.keys())  # Reset the keys every time iter is called
        return self

    def __next__(self):
        with self._lock:  # Acquire the lock
            if self._index < len(self._keys):
                key = self._keys[self._index]
                value = self.__dict__[key]
                self._index += 1
                return key, value
            else:
                raise StopIteration

    def __contains__(self, item):
        return True if hasattr(self, item) else False

    def __getitem__(self, key):
        if key in self:
            return getattr(self, key)
        else:
            raise KeyError(f"Key '{key}' not found.")

    def __setitem__(self, key, value):
        if key in self:
            setattr(self, key, value)
        else:
            raise KeyError(f"Key '{key}' not found.")

    def get_values(self):
        return {name: self[name] for name in self.get_names()}

    def get_names(self):
        return [name for name in self.__dict__.keys() if not name.startswith('_')]

    def load_settings_from_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                loaded_dict = json.load(file)
        except FileNotFoundError:
            return

        for key, value in loaded_dict.items():
            if hasattr(self, key):
                setattr(self, key, self.convert_type_string(value))

    def save_settings_to_file(self, file_name):
        with open(file_name, 'w') as file:
            json.dump(self.get_values(), file, indent=4)

    @staticmethod
    def convert_type_string(s):
        if not isinstance(s, str):
            return s

        # Check for None
        if s.lower() == 'none':
            return None

        # Check for boolean values
        if s.lower() == 'true':
            return True

        if s.lower() == 'false':
            return False

        # Check for integer
        try:
            int_value = int(s)
            return int_value
        except ValueError:
            pass

        # Check for float
        try:
            float_value = float(s)
            return float_value
        except ValueError:
            pass

        # If none of the above, return 'str'
        return s

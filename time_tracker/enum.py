from enum import Enum


class StringEnum(Enum):
    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

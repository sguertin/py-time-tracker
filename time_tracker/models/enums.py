from enum import Enum


class StringEnum(Enum):
    def __eq__(self, other: "StringEnum"):
        return str(self.value) == str(other.value)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

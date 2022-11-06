from abc import ABCMeta, abstractmethod
from typing import Any

EMPTY = ""


class View(metaclass=ABCMeta):
    title: str
    layout: list
    size: tuple[int, int] = None

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "run") and callable(subclass.run)) or NotImplemented

    @abstractmethod
    def run(self) -> Any:
        raise NotImplementedError(self.run)

from abc import ABCMeta, abstractmethod

from time_tracker.constants import Events


class View(metaclass=ABCMeta):
    title: str
    layout: list
    size: tuple[int, int] = None

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "run") and callable(subclass.run)) or NotImplemented

    @abstractmethod
    def run(self, close: bool = True) -> tuple[Events, dict[str, str]]:
        raise NotImplementedError(self.run)

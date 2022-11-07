from abc import ABCMeta, abstractmethod

from time_tracker.models.settings import Settings


class ISettingsProvider(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "ISettingsProvider"):
        return (
            hasattr(subclass, "get_settings") and callable(subclass.get_settings)
        ) or NotImplemented

    @abstractmethod
    def get_settings(self) -> Settings:
        raise NotImplementedError(self.get_settings)

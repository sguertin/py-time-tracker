from abc import ABCMeta


class IAuthenticationProvider(meta=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IAuthenticationProvider"):
        return (
            (hasattr(subclass, "clear_auth") and callable(subclass.clear_auth))
            and (hasattr(subclass, "get_auth") and callable(subclass.get_auth))
            and (hasattr(subclass, "set_auth") and callable(subclass.set_auth))
            or NotImplemented
        )

    def clear_auth(self) -> None:
        raise NotImplementedError(self.clear_auth)

    def get_auth(self) -> str:
        raise NotImplementedError(self.get_auth)

    def set_auth(self, user_name: str, password: str) -> None:
        raise NotImplementedError(self.set_auth)

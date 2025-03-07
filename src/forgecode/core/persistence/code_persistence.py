from abc import ABC, abstractmethod

class CodePersistence(ABC):
    @abstractmethod
    def save(self, id: str, code: str) -> None:
        pass

    @abstractmethod
    def load(self, id: str) -> str | None:
        pass
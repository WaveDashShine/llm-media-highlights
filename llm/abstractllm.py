from abc import ABC, abstractmethod


class AbstractLlm(ABC):

    @abstractmethod
    def get_highlights(self, filename: str) -> str:
        pass

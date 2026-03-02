from abc import ABC, abstractmethod

class BaseParser(ABC):

    @abstractmethod
    def parse(self, file_path: str) -> list[dict]:
        """
        Returns list of:
        {
            "text": str,
            "metadata": dict
        }
        """
        pass


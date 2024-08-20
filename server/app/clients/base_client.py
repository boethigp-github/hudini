from abc import ABC, abstractmethod

class BaseClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        pass

    @abstractmethod
    def get_available_models(self):
        pass

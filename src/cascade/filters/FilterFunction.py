from abc import ABC, abstractmethod

class FilterFunction(ABC):
    def __call__(self, *args, **kwargs):
        return self.filter(*args)

    @abstractmethod
    def filter(self, context) -> bool:
        pass

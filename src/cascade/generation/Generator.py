from abc import ABC, abstractmethod

class Generator(ABC):
    """
    The abstract base class for all generators. This class is designed to be inherited by all generators.
    """

    @abstractmethod
    def generate(self, context, input_path, output_path):
        pass

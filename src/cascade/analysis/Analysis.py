from abc import ABC, abstractmethod
from cascade.analysis.executor.Execution import Execution
from cascade.generation.Generation import Generation

class Analysis(ABC):
    """
    The abstract base class for all analysis classes.
    """
    def __init__(self, generator: Generation, executor: Execution):
        self.generator = generator
        self.executor = executor

    @abstractmethod
    def analyze(self, data, input_path, output_path):
        pass

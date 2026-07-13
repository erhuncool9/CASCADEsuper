import os

from cascade.analysis.Analysis import Analysis
from cascade.analysis.executor.Execution import Execution
from cascade.generation.Generation import Generation

from cascade.utils.Utils import save_dicts_list_to_json

class EmptyAnalysis(Analysis):
    """
    This is a placeholder Analysis class that does nothing.
    """
    def __init__(self, generator: Generation, executor: Execution):
        super().__init__(generator, executor)


    def analyze(self, data, input_path, output_path):
        """
        This analysis should do nothing. but to save the extracted and filtered data directly.
        can be used as a placeholder if only extraction and filtering should be tested.
        """
        save_dicts_list_to_json(data, os.path.join(output_path, "analyzed.json"))

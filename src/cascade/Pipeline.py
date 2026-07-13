import os

from cascade.extraction.Extraction import Extraction
from cascade.filters.Filter import Filter
from cascade.analysis.Analysis import Analysis
from cascade.utils.Utils import load_json_from_path


class Pipeline():
    def __init__(self, extraction: Extraction, _filter: Filter, analysis: Analysis, setup_config: dict):
        """
        The main pipeline object. Calls "extract" and "analyse" in an appropriate manner.
        is usually build through Pipeline_Factory
        :param extraction: the specific instantiated Extraction object that is used for extraction
        :param analysis: the specific instantiated analysis object
         :param setup: a dictionary that contains the names of the specific instances used
         for extraction, analysis and the objects inside of them,
        """
        self.extraction = extraction
        self._filter = _filter
        self.analysis = analysis
        self.setup_config = setup_config

    def execute(self, input_path, output_path) -> None:
        """
        This executes the entire pipline. First extract() from the extraction object is called.
        he output of that is passed to the analysis object. and analyze is executed.

        These specific objects handle what the specific operations do and any things like temporary or
        intermediate saving, which type of analyses should be done and the generator that the analysis uses.
        """
        if not os.path.exists(os.path.join(output_path, "analyzed.json")):
            print("Extraction started")
            data = self.extraction.extract(input_path, output_path)
            print("Extraction finished. Extracted: ", len(data))

            print("Filtering started")
            filtered_data = self._filter.filter_all(data)
            print("Filtering finished. Remaining: ", len(filtered_data))

        else:
            print("Found analyzed results, will skip extraction and filtering")
            # generated artifacts for the same dataset can be saved to avoid repeated generation of code and tests.
            temp_data = load_json_from_path(os.path.join(output_path, "analyzed.json"))
            filtered_data = []
            if temp_data:
                filtered_data = temp_data

        if not filtered_data:
            print("No data to analyze")
            return

        print("Analysis started")
        self.analysis.analyze(filtered_data, input_path, output_path)
        print("Analysis finished")


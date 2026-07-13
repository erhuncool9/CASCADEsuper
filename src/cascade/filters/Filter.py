import copy
from typing import List

from cascade.filters.FilterFunction import FilterFunction
from cascade.filters.NoFilter import NoFilter


class Filter:
    """
    This class is used to filter a list of dictionaries based on a list of specified filter functions.
    """
    def __init__(self, filter_functions: List[FilterFunction]):
        self.filter_functions = filter_functions
        self.filter_functions.append(NoFilter())

    def filter_all(self, data: List[dict]) -> List[dict]:
        """
        This method filters the data based on the filter functions. It returns a list of dictionaries that passed all filter functions.
        :param data: List of dictionaries that should be filtered
        :return: List of dictionaries that pass all filters provided in the self.filter_functions list
        """
        filtered_data = [x for x in data if all([f(copy.deepcopy(x)) for f in self.filter_functions])]

        return filtered_data


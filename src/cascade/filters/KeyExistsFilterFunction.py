from cascade.filters.FilterFunction import FilterFunction
from cascade.utils.Utils import get_value_from_context


class KeyExistsFilterFunction(FilterFunction):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.found = False

    def callback(self, key):
        self.found = False

    def filter(self, context) -> bool:
        self.found = True

        get_value_from_context(self.key, context, self.callback)

        return self.found

from cascade.filters.FilterFunction import FilterFunction

class NoTestsFilterFunction(FilterFunction):
    def __init__(self):
        super().__init__()

    def filter(self, context) -> bool:
        return "tests" in context

from cascade.filters.FilterFunction import FilterFunction


class NoFilter(FilterFunction):
    def __init__(self):
        super().__init__()

    def filter(self, context):
        return True

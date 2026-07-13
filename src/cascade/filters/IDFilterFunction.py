from cascade.filters.FilterFunction import FilterFunction


class IDFilterFunction(FilterFunction):
    def __init__(self, id_list):
        """
        A filter that is used to check if a key contains a certain content.

        Keys are evaluated hierarchically, so to check "name" in {"signature": {"name": "test"}}, the key would be
        "signature.name".

        :param key: The dictionary key in question
        :param content: The string that is supposed to be contained
        :param iterate: Sets if the value should be iterated if it is a list (default True)
        :param re: Sets the matching type to regex matching (default False)
        :param invert: Inverts the return value if the value is contained (default False)
        :param return_value_if_not_exists: Sets the value to concern if anything goes wrong during the search (default False)
        """

        super().__init__()
        self.id_list = id_list

    def filter(self, context) -> bool:
        return context["id"] in self.id_list
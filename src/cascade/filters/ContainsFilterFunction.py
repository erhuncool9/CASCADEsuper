import re

from cascade.filters.FilterFunction import FilterFunction
from cascade.utils import Utils


class ContainsFilterFunction(FilterFunction):
    def __init__(self, key, content, iterate=True, re=False, invert=False, return_value_if_not_exists=False):
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
        self.return_value_if_not_exists = return_value_if_not_exists
        self.invert = invert
        self.re = re
        self.iterate = iterate
        self.content = content
        self.key = key

    def filter(self, context) -> bool:
        value = Utils.get_value_from_context(self.key, context, lambda x: None)
        if value == None:

            return self.return_value_if_not_exists

        if isinstance(value, list):
            if self.iterate:
                for sub_value in value:
                    if self.check_if_contains(sub_value, self.content):
                        return not self.invert
                return self.invert

            else:
                return self.return_value_if_not_exists
        else:

            return self.check_if_contains(value, self.content) != self.invert

    #missing return here

    def check_if_contains(self, value, content):
        if self.re:
            found = bool(re.search(content, value))
        else:
            found = content in value
        return found


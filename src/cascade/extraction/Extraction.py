from abc import ABC, abstractmethod
from typing import List

class Extraction(ABC):
    @abstractmethod
    def extract(self, input_path, output_path) -> List[dict]:
        """
        This is the main method of the Extraction module.
        It gets an input path which could be for a root directory of an entire project or a dataset file or a jar.
        It then should extract functions and other required data from there.

        These should then be returned as a list of dictionaries but also saved as a json file to the output path.
        Either with the generic name such as "extracted.json" or with the name provided in the path if it ends with ".json".
        This could also be used to append to an existing file.

        The expected output format for one function is
        {
            "doc" : str  - the docstring of the function,
            "id" : str or int - depending on the use case a unique id to later identify the function,
            "signature" : {
                "name" : str - the simple name of the function,
                "returns" : str - return type of the function,
                "params" : list of str - parameters, including types (if existent) ach as a string,
                "modifier" : list of str,
                "annotations": list of str,
                "generics" list of str
                }
            "language" : str   - #e.g. python or java
            "parent" : {
                "name" : str,
                "doc" : str,
                "imports" : list of str,
                "other_methods" : list of dict    these dicts should contain {doc:str, signature:dict, code:str},
                "variables" : list of str   - global variables of the class that could be used by the function under test,
                "generics" : list of str
                }
            "code" : str - the body of the function
            "code_file_path" : str - path to the file where the code resides in (relative to root),
            "called_functions" : list of str - full function call of the functions that are called inside of the original 'code',
            "tests" :  str - The complete content of a test file,
            "test_imports" : list of str - imports of the test file,
            "test_file_path" : str - path to the test file (relative to root),
        }

        Note that depending on the 'Analysis' and 'Generate' implementations not all of these fields need to be filled.
        And that some languages might have additional fields

        You can use the implementation 'json_Extraction' and its extract() method to check whether
        the file already exists in the output path and just load this one instead.
        """
        pass

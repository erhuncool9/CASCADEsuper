from cascade.extraction.Extraction import Extraction
from cascade.extraction.JsonExtraction import JsonExtraction
from typing import List, Dict
from cascade.utils.Utils import save_dicts_list_to_json
import subprocess
import os


class JavaExtraction(Extraction):
    def __init__(self, pattern: str = "/%cTest.java"):
        """
        A class which enables extracting Java projects.

        :param pattern: A string which is used to match Test classes to source classes, supports '%c' as a meta token
            which will be replaced by the class name (e.g., class HashMap with pattern '%cTest.java' will be matched to
            HashMapTest.java)
        """
        super().__init__()
        self.pattern = pattern


    def extract(self, input_path, output_path) -> List[Dict[str, any]]:
        """
        Extracts a java class hierarchy from the source folder that the input path points to.

        For typical java package structures point it to the directory which contains both the source and the test
        directory.

        If there already is an "extracted.json" in the output folder, loads that instead.

        :param input_path: The path to the jar/source folder
        :param output_path:
        :return:
        """
        json_extractor = JsonExtraction()
        extracted = json_extractor.extract(input_path, output_path)
        if extracted:
            return extracted

        my_path = os.path.dirname(__file__)
        subprocess.run(
            ["java", "-Xmx12G", "-jar", os.path.join(my_path, "..", "resources", "tools", "JavaExtractor.jar"),
             "ext",
             input_path,
             self.pattern,
             output_path]
        )
        extracted = json_extractor.extract(input_path, output_path)

        count = 0
        for e in extracted:
            e["id"] = count
            count += 1
            del e["root_path"]


        save_dicts_list_to_json(extracted, os.path.join(output_path, "extracted.json"))

        return extracted

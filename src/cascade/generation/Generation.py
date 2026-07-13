import copy

from cascade.generation.Generator import Generator


class Generation:
    """
    This is the wrapper class for all types of generators
    """
    def __init__(self, code_generator: Generator, test_generator: Generator, doc_generator: Generator):
        """
        Constructor for the general Generation class that takes in three generators as parameters and assigns them to the class.

        if one is not needed for the analysis on hand the 'EmptyGenerator' class can be used instead.

        :param code_generator: The generator that generates code
        :param test_generator: The generator that generates tests
        :param doc_generator: The generator that generates documentation
        """

        self.code_generator = code_generator
        self.test_generator = test_generator
        self.doc_generator = doc_generator

    def generate_code(self, context, input_path, output_path):
        """
        code generation method
        :param input_path:
        """
        context_ = copy.deepcopy(context)
        code, response = self.code_generator.generate(context_, input_path, output_path)
        del context_
        return code, response

    def generate_tests(self, context, input_path, output_path):
        context_ = copy.deepcopy(context)
        tests, response = self.test_generator.generate(context_, input_path, output_path)
        del context_
        return tests, response

    def generate_doc(self, context, input_path, output_path):
        context_ = copy.deepcopy(context)
        doc, response = self.doc_generator.generate(context_, input_path, output_path)
        del context_
        return doc, response

    def repair_tests(self, context, input_path, output_path, errors, key):
        context_ = copy.deepcopy(context)
        tests, response = self.test_generator.repair(context_, input_path, output_path, errors, key)
        del context_
        return tests, response

    def repair_code(self, context, input_path, output_path, errors, key):
        context_ = copy.deepcopy(context)
        code, response = self.code_generator.repair(context_, input_path, output_path, errors, key)
        del context_
        return code, response
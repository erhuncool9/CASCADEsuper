

class ExecutionResults():
    """
    a return type for the executor.
    It contains:
        - the individual test results of the execution by name,
        - the numbers of failing/passing and erroring tests cases,
        - the compilation errors,
        - the parsed file which is the stdout nad stderr caught during execution.

        - and all matches in this parsed file (compiler errors, test overview, xml blocks)
    """
    def __init__(self):
        self.results = ([],[],[])
        self.results_numbers = (0,0,0)
        self.comp_errors = None
        self.parsed_file = ""

        self.comp_error_matches = []
        self.test_overview_matches = []
        self.xml_blocks = []

    def __str__(self):
        string = (f"---------------------------EXECUTIONResults:\n----Results:\n{self.results}\n"
                  f"----Numbers:\n{self.results_numbers}\n----Comp Errors:\n{self.comp_errors}\n"
                  f"----Parsed File:\n{self.parsed_file}\n----Comp Error Matches:\n{self.comp_error_matches}\n"
                  f"----Test Overview Matches:\n{self.test_overview_matches}\n----XML Blocks:\n{self.xml_blocks}\n"
                  "EXECUTIONResults---------------------\n"
                  )

        return string
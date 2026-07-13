from abc import ABC, abstractmethod


class Builder(ABC):
    """
    Abstract base class for building and setting up the environment and Project
    for code and test execution
    """

    def __init__(self, test_pattern="", eval_function=None, image=""):
        """
        Initializes the Builder.
        :param test_pattern: naming Pattern for identifying test output in the docker container.
        :param eval_function: Function to evaluate the test results.
        :param image: Docker image to be used for the environment.
        """
        self.test_pattern = test_pattern
        self.eval_function = eval_function
        self.image = image


    def set_up(self, temp_dir, context, output_path):
        """
        Sets up the environment for execution.

        :param temp_dir: Temporary directory for setup.
        :param context: Contextual information for the setup.
        :param output_path: Path to the output files.

        :return: Boolean indicating success or failure of the setup.
        """
        return True


    @abstractmethod
    def tear_down(self, context):
        """
        Tears down the environment after execution.

        :param context: Contextual information for the teardown.
        """
        pass
import re
from cascade.analysis.executor.ExecutionResults import ExecutionResults
from cascade.analysis.executor.builders.Builder import Builder
from cascade.utils.DockerizedWrapper import DockerizedWrapper
import xml.etree.ElementTree as ET

class MavenBuilder(Builder):
    """Build/test executor for Maven projects running inside Docker.

    `MavenBuilder` wires three concerns together:

    - It defines the shell command template used by `Builder` to run selected
      tests (`-Dtest="%t"`) with a timeout.
    - It captures both Maven console output and Surefire XML report content into
      one stream so `eval_function` can parse summary and per-test outcomes.
    - It manages a temporary derived Docker image used during analysis
      (`set_up`) and cleans it up afterwards (`tear_down`).

    Parsing is intentionally tolerant: compilation errors and test summaries are
    extracted with regexes, and XML parsing errors are treated as non-fatal so
    callers still receive partial `ExecutionResults`.
    """

    def __init__(self, new_image_name, maven_args, set_up_maven_command, set_up_maven_args, image, timeout=300):
        super().__init__(
            #test_pattern = f"echo \"[INFO] Tests run: 0, Failures: 0, Errors: 0, Skipped: 0\" > out; timeout {timeout} mvn test {maven_args} -Dtest=\"%t\" -DfailIfNoTests=false -Dsurefire.reportsDirectory=target/surefire-reports > output 2>&1; cat output > out; cat target/surefire-reports/TEST-*.xml >> out; cat output",

            test_pattern = (f"echo \"[INFO] Tests run: 0, Failures: 0, Errors: 0, Skipped: 0\" > out; "
                            f"timeout {timeout} mvn clean test {maven_args} -Dtest=\"%t\" -DfailIfNoTests=false "
                            f"-Dsurefire.reportsDirectory=target/surefire-reports > output 2>&1; status=$?; cat output > out; "
                            f"find . -path \"*/target/surefire-reports/TEST-*.xml\" -type f "
                            f"-exec cat {{}} \\; >> out; echo \"[INFO] Exit code: $status\" >> out;"
                            f"cat output"
                            ),

            eval_function = self.eval_function,
            image = new_image_name
        )
        self.old_image_name = image
        self.set_up_maven_args = set_up_maven_args
        self.set_up_maven_command = set_up_maven_command


    def eval_function(self, x):
        """
        Parse combined Maven/Surefire output into an `ExecutionResults` object.

        The expected input is the exact command output produced by this builder's
        `test_pattern`: Maven logs plus concatenated `TEST-*.xml` files.

        Parsing is performed in stages:

        1. Detect compilation errors in Maven logs.
        2. Extract the aggregate test summary line (`Tests run: ...`).
        3. Parse Surefire XML blocks to identify passed/failed/errored test names.

        If no summary line is found, the method returns early with only the
        fields gathered so far. XML parsing failures are logged and ignored, so
        callers can still inspect partial data from `ExecutionResults`.

        :param x: Full stdout/stderr text captured from container execution.
        :return: Populated `ExecutionResults` instance.
        """
        results = ExecutionResults()
        results.parsed_file = x

        # First Catch Compilation Errors
        comp_matches = re.findall(r'\[ERROR\] COMPILATION ERROR :[\s\S]*?\[INFO\] -*\n(.*?)\[INFO\]', x, re.DOTALL)

        if comp_matches:
            results.comp_error_matches = comp_matches
            results.comp_errors = comp_matches[-1].strip()

        # get general test results
        test_overview_matches = re.search(r"Tests run: \d+, Failures: \d+, Errors: \d+, Skipped: \d+, Time", x)
        results.test_overview_matches = test_overview_matches

        if not test_overview_matches:
            return results

        matched_line = test_overview_matches[0]
        run_fail_err_skip = list(map(int, re.findall(r"\d+", matched_line)))
        total_tests = run_fail_err_skip[0]

        passed_count = total_tests - sum(run_fail_err_skip[1:])
        failed_count = run_fail_err_skip[1]
        errored_count = run_fail_err_skip[2]

        results.results_numbers = passed_count, failed_count, errored_count

        if total_tests == 0:
            return results

        # get specific test results
        xml_blocks = re.findall(r'(<\?xml.*?</testsuite>)', x, re.DOTALL)
        results.xml_blocks = xml_blocks


        passed = []
        failed = []
        errored = []

        for xml_block in xml_blocks[::-1]:
            passed = []
            failed = []
            errored = []

            try:
                root = ET.fromstring(xml_block)

                # Loop over each <testcase> element.
                for testcase in root.findall('testcase'):
                    test_name = testcase.attrib.get('name')
                    # If a <failure> or <error> tag exists as a child, mark accordingly.
                    if testcase.find('failure') is not None:
                        failed.append(test_name)
                    elif testcase.find('error') is not None:
                        errored.append(test_name)
                    else:
                        passed.append(test_name)

            except Exception as e:
                print("Error parsing XML:", e)

            if len(passed) == passed_count and len(failed) == failed_count and len(errored) == errored_count:
                break

        results.results = passed, failed, errored

        return results


    def set_up(self, temp_dir, _, output_path):
        """
        Create the temporary Docker image used for Maven test execution.

        The setup command runs inside the base image (`self.old_image_name`) and
        can be used for actions such as dependency pre-fetching or project
        preparation. The resulting image is stored as `self.image` for subsequent
        test runs.

        :param temp_dir: Directory mounted into Docker as execution context.
        :param _: Unused placeholder to satisfy the builder interface.
        :param output_path: Path where setup logs/artifacts are written.
        :return: Wrapper-specific setup result from `DockerizedWrapper.setup_image`.
        """
        wrapper = DockerizedWrapper()
        dock_context = {
            "image": self.old_image_name,
            "new_image": self.image,
            "directory": temp_dir,
            "command": f"timeout 180 mvn {self.set_up_maven_command} {self.set_up_maven_args}; RET=$?; rm -rf ../root/*; exit $RET;",
        }
        return wrapper.setup_image(dock_context, output_path)


    def tear_down(self, _):
        """Remove the temporary Docker image created during `set_up`."""
        wrapper = DockerizedWrapper()
        dock_context = {
            "new_image": self.image,
        }
        wrapper.remove_image(dock_context)


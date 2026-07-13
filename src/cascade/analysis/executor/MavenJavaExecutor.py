from cascade.analysis.executor.JavaExecutor import JavaExecutor
from cascade.analysis.executor.builders.MavenBuilder import MavenBuilder

import uuid

class MavenJavaExecutor(JavaExecutor):
    """
    The specific JavaExecutor for Maven projects
    """
    def __init__(self, debug=False, maven_args="", set_up_maven_command="test", set_up_maven_args="", image="maven"):
        """
        The constructor for the MavenJavaExecutor.

        :param debug: A boolean which indicates if the executor should run in debug mode
        :param maven_args: Additional arguments for the mvn command
        :param set_up_maven_command: The command to set up and start mvn.  usually 'test'
        :param set_up_maven_args: Additional arguments for the mvn set up command
        :param image: The base image to use for the docker container
        """

        # generate a unique ID to give the new image a unique name. This is necessary to avoid conflicts with other images especially when multithreading
        image_name_id = str(uuid.uuid4())

        # these arguments should be working for all maven projects and some are necessary to avoid errors
        #standard_java_args = " -fae -Drat.skip=true -DforkMode=never -Dsurefire.failIfNoSpecifiedTests=false"
        standard_java_args = " -fae -Drat.skip=true -DforkMode=never -Dsurefire.failIfNoSpecifiedTests=false -DforkCount=1 -DreuseForks=true -Danimal.sniffer.skip=true"
        if maven_args == "":
            maven_args = standard_java_args
        if set_up_maven_args == "":
            set_up_maven_args = standard_java_args

        super().__init__(debug,
                         MavenBuilder(
                             new_image_name=image_name_id,
                             maven_args=maven_args,
                             image=image,
                             set_up_maven_command=set_up_maven_command,
                             set_up_maven_args=set_up_maven_args,
                             timeout=300
                         ))

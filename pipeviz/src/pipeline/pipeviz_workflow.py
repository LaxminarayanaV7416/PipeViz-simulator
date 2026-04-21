import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

from loguru import logger

from src.config import BASE_PATH
from src.enum_vault.workflow_enums import (
    DockerFileNamesEnum,
    RunnableCommands,
    SupportedProgrammingLanguagesEnum,
    WorkflowPaths,
)


class PipeVizWorkflow:
    def __init__(self, programming_language: SupportedProgrammingLanguagesEnum):
        """
        input args
            programming_language: SupportedProgrammingLanguagesEnum - The programming language to use for the workflow.

            steps it will do to get the Assembly code as object dump
            - Gets the file/code from frontend and create a new file in the runs directory.
                - for now no frontend so lets try to use a local file.
            - copy the related dockerfile to the runs directory.
            - run the object dump generation command using docker.
            - copy the output object dump file to the runs directory.
        """
        self._id = uuid4()
        self._paths = WorkflowPaths(BASE_PATH)
        self._programming_language = programming_language
        self._commands = RunnableCommands()

    @property
    def run_path(self) -> Path:
        path = self._paths.runs / str(self._id)
        if not path.exists():
            # now create a new directory
            path.mkdir(parents=True, exist_ok=True)
        return path

    def move_files(self, source: Path, destination: Path) -> bool:
        try:
            shutil.copy(source, destination)
            return True
        except Exception as e:
            logger.error(e)
            return False

    def run_shell_command(self, command: list | str) -> tuple[bool, str]:
        try:
            response = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            if self.validate_shell_execution(response):
                return True, response.stdout
            else:
                return False, response.stderr
        except subprocess.CalledProcessError as error:
            logger.error(error)
            return False, str(error)

    def validate_shell_execution(
        self, response: subprocess.CompletedProcess | str
    ) -> bool:
        if isinstance(response, subprocess.CompletedProcess):
            return response.returncode == 0
        return False

    def generate_asembly_code(
        self,
        code_path: Path,
    ) -> tuple[bool, str | Path]:
        asm_path = self.run_path / "main.asm"
        program_file_name = code_path.name
        if self._programming_language == SupportedProgrammingLanguagesEnum.RUST:
            src_path = self._paths.rust_docker_file
            docker_file_name = DockerFileNamesEnum.RUST
        elif self._programming_language == SupportedProgrammingLanguagesEnum.C:
            src_path = self._paths.c_docker_file
            docker_file_name = DockerFileNamesEnum.C
        else:
            src_path = self._paths.cpp_docker_file
            docker_file_name = DockerFileNamesEnum.CPP

        # step 1: create the run directory
        # and move the required files to the run directory
        file_name = src_path.name
        self.move_files(src_path, self.run_path / file_name)

        # step 2: move the code file as well
        file_name = code_path.name
        self.move_files(code_path, self.run_path / file_name)

        # step 3: do the docker build
        docker_build_command = self._commands.docker_build(
            str(self._id),
            self.run_path / docker_file_name.value,
            program_file_name,
        )
        executed, response = self.run_shell_command(docker_build_command)
        if not executed:
            return False, response

        # step 4: create docker so that we can actually copy the asm
        docker_create_command = self._commands.docker_create(str(self._id))
        executed, response = self.run_shell_command(docker_create_command)
        if not executed:
            return False, response

        container_id = response.strip()  # figure out its true or not
        logger.info("We generated the container id as it is: ", container_id)

        # step 5: copy generated assembly from the built docker file
        docker_copy_command = self._commands.docker_copy(
            container_id, self._programming_language, str(self.run_path)
        )
        executed, response = self.run_shell_command(docker_copy_command)
        if not executed:
            return False, response

        # # step 6: remove the docker container
        # docker_remove_command = self._commands.docker_remove(container_id)
        # executed, _ = self.run_shell_command(docker_remove_command)
        # if not executed:
        #     return False, response

        # step 7: clean docker image from cache
        docker_image_delete_command = self._commands.docker_image_delete(str(self._id))
        executed, _ = self.run_shell_command(docker_image_delete_command)
        if not executed:
            return False, response

        return True, asm_path


if __name__ == "__main__":
    workflow = PipeVizWorkflow(SupportedProgrammingLanguagesEnum.CPP)
    result = workflow.generate_asembly_code(workflow._paths.cpp_mock_path)
    logger.info(result)

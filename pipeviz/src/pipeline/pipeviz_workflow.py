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

    def execute_command(self, cmd_list: list[str]) -> tuple[bool, list[str]]:
        """Executes a command, logs output live, and fails on non-zero exit."""
        result: list[str] = []
        try:
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            if process.stdout:
                for line in process.stdout:
                    temp = line.rstrip("\n")
                    result.append(temp)
                    if temp:
                        logger.info(temp)

            return_code = process.wait()

            if return_code != 0:
                logger.error(f"Failed! Process exited with code {return_code}")
                return False, result

            return True, result

        except Exception as e:
            logger.exception(f"An exception occurred running the command: {e}")
            return False, result

    def clean(self) -> None:
        if self.run_path.exists():
            shutil.rmtree(self.run_path)

    def generate_asembly_code(
        self,
        code_path: Path,
    ) -> tuple[bool, list[str] | Path]:
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
        executed, response = self.execute_command(docker_build_command)
        if not executed:
            return False, response

        # step 4: create docker so that we can actually copy the asm
        docker_create_command = self._commands.docker_create(str(self._id))
        executed, response = self.execute_command(docker_create_command)
        if not executed:
            return False, response

        container_id = response[0].strip()  # figure out its true or not
        logger.info("We generated the container id as it is: ", container_id)

        # step 5: copy generated assembly from the built docker file
        docker_copy_command = self._commands.docker_copy(
            container_id, self._programming_language, str(self.run_path)
        )
        executed, response = self.execute_command(docker_copy_command)
        if not executed:
            return False, response

        # step 7: clean docker image from cache
        docker_image_delete_command = self._commands.docker_image_delete(str(self._id))
        executed, response = self.execute_command(docker_image_delete_command)
        if not executed:
            return False, response

        return True, asm_path


if __name__ == "__main__":
    workflow = PipeVizWorkflow(SupportedProgrammingLanguagesEnum.RUST)
    result = workflow.generate_asembly_code(workflow._paths.rust_mock_path)
    logger.info(result)

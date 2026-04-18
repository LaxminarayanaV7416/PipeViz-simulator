import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

from src.enum_vault.workflow_enums import (
    RunnableCommands,
    SupportedProgrammingLanguagesEnum,
    WorkflowPaths,
)

BASE_PATH = Path(__file__).parent


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
        if path.exists():
            # delete existing directory
            shutil.rmtree(path)
        # now create a new directory
        path.mkdir(parents=True, exist_ok=True)
        return path

    def move_files(self, source: Path, destination: Path) -> bool:
        try:
            shutil.copy(source, destination)
            return True
        except Exception as e:
            print(e)
            return False

    def run_shell_command(
        self, command: list | str
    ) -> tuple[bool, subprocess.CompletedProcess | None]:
        try:
            response = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            return True, response
        except subprocess.CalledProcessError as error:
            print(error)
            return False, None

    def generate_asembly_code(
        self, programming_language: SupportedProgrammingLanguagesEnum
    ):
        # step 1: create the run directory
        # and move the required files to the run directory
        if programming_language == SupportedProgrammingLanguagesEnum.RUST:
            src_path = self._paths.rust_docker_file
        elif programming_language == SupportedProgrammingLanguagesEnum.PYTHON:
            src_path = self._paths.python_docker_file
        else:
            src_path = self._paths.c_cpp_docker_file

        self.move_files(src_path, self.run_path)
        

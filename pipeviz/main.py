import shutil
from pathlib import Path
from uuid import uuid4

from src.enum_vault.workflow_enums import (
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

    @property
    def run_path(self) -> Path:
        path = self._paths.runs / str(self._id)
        if path.exists():
            # delete existing directory
            shutil.rmtree(path)
        # now create a new directory
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def generate_asembly_code(self):
        

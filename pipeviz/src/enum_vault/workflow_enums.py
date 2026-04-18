from enum import StrEnum
from pathlib import Path


class SupportedProgrammingLanguagesEnum(StrEnum):
    RUST = "rust"
    C_CPP = "c_cpp"
    PYTHON = "python"


class SupportedFileExtensionsEnum(StrEnum):
    PYTHON = "py"
    RUST = "rs"
    CPP = "cpp"
    C = "c"


class DockerFileNamesEnum(StrEnum):
    RUST = "Dockerfile.rust"
    PYTHON = "Dockerfile.python"
    C_CPP = "Dockerfile.c_cpp"


class RunnableCommands:
    def docker_build(self, image_tag: str) -> list[str]:
        return ["docker", "build", "--no-cache", "-t", image_tag]

    def docker_create(self, image_tag: str) -> list[str]:
        return ["docker", "create", image_tag]

    def docker_copy(
        self,
        container_id: str,
        programming_language: SupportedProgrammingLanguagesEnum,
        destination_path: Path,
    ) -> list[str]:
        if programming_language == SupportedProgrammingLanguagesEnum.RUST:
            result = ["docker", "cp", f"{container_id}:/app/main.asm", destination_path]
        elif programming_language == SupportedProgrammingLanguagesEnum.C_CPP:
            result = ["docker", "cp", f"{container_id}:/app/main.asm", destination_path]
        elif programming_language == SupportedProgrammingLanguagesEnum.PYTHON:
            result = ["docker", "cp", f"{container_id}:/app/main.asm", destination_path]
        return result

    def docker_remove(self, container_id: str) -> list[str]:
        return ["docker", "rm", container_id, ">/dev/null"]


class WorkflowPaths:
    def __init__(self, base_path: Path):
        self._base_path = base_path

    @property
    def assembly_assets(self) -> Path:
        return self._base_path / "assembly_assets"

    @property
    def runs(self) -> Path:
        return self._base_path / "runs"

    @property
    def rust_docker_file(self) -> Path:
        return self.assembly_assets / "rust.dockerfile"

    @property
    def python_docker_file(self) -> Path:
        return self.assembly_assets / "python.dockerfile"

    @property
    def c_cpp_docker_file(self) -> Path:
        return self.assembly_assets / "c_cpp.dockerfile"

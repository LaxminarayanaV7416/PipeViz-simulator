from enum import StrEnum
from pathlib import Path


class SupportedProgrammingLanguagesEnum(StrEnum):
    RUST = "rust"
    C = "c"
    CPP = "cpp"


class SupportedFileExtensionsEnum(StrEnum):
    RUST = "rs"
    CPP = "cpp"
    C = "c"


class DockerFileNamesEnum(StrEnum):
    RUST = "rust.dockerfile"
    C = "c.dockerfile"
    CPP = "cpp.dockerfile"


class RunnableCommands:
    def docker_build(
        self, image_tag: str, file_name: Path, program_file_name: str
    ) -> list[str]:
        return [
            "docker",
            "build",
            "--no-cache",
            "-f",
            str(file_name),
            "-t",
            image_tag,
            "--build-arg",
            f"PROGRAM_FILE_NAME={program_file_name}",
            str(file_name.parent),
        ]

    def docker_create(self, image_tag: str) -> list[str]:
        return ["docker", "create", image_tag]

    def docker_copy(
        self,
        container_id: str,
        programming_language: SupportedProgrammingLanguagesEnum,
        destination_path: Path | str,
    ) -> list[str]:
        result = None
        if programming_language == SupportedProgrammingLanguagesEnum.RUST:
            result = ["docker", "cp", f"{container_id}:/app/main.asm", destination_path]
        elif programming_language == SupportedProgrammingLanguagesEnum.C:
            result = ["docker", "cp", f"{container_id}:/app/main.asm", destination_path]
        elif programming_language == SupportedProgrammingLanguagesEnum.CPP:
            result = ["docker", "cp", f"{container_id}:/app/main.asm", destination_path]
        return result

    def docker_remove(self, container_id: str) -> list[str]:
        return ["docker", "rm", container_id, ">/dev/null"]

    def docker_image_delete(self, image_tag: str) -> list[str]:
        return ["docker", "image", "rm", "-f", image_tag]


class WorkflowPaths:
    def __init__(self, base_path: Path):
        self._base_path = base_path

    @property
    def assembly_assets(self) -> Path:
        return self._base_path / "assembly_assets"

    @property
    def mock_path(self) -> Path:
        return self._base_path / "mock"

    @property
    def runs(self) -> Path:
        path = (self._base_path / "runs").resolve()
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def rust_docker_file(self) -> Path:
        return self.assembly_assets / "rust.dockerfile"

    @property
    def c_docker_file(self) -> Path:
        return self.assembly_assets / "c.dockerfile"

    @property
    def cpp_docker_file(self) -> Path:
        return self.assembly_assets / "cpp.dockerfile"

    @property
    def rust_mock_path(self) -> Path:
        return self.mock_path / "test-fib.rs"

    @property
    def cpp_mock_path(self) -> Path:
        return self.mock_path / "test-fib.cpp"

    @property
    def c_mock_path(self) -> Path:
        return self.mock_path / "test-fib.c"

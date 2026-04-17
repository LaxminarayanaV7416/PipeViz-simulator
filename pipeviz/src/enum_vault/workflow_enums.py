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

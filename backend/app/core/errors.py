"""Domain errors raised by the backend."""

from pathlib import Path


class InvalidContentError(Exception):
    """A file in content/ is missing, malformed or breaks the content schema."""

    def __init__(self, path: Path, problem: str) -> None:
        super().__init__(f"{path}: {problem}")
        self.path = path
        self.problem = problem

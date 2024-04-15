"""Github Actions helper functions."""

import os
from collections.abc import MutableMapping
from functools import cached_property
from pathlib import Path
from typing import Dict, Iterator

INPUT_PREFIX = "INPUT_"


class InputProxy(MutableMapping[str, str]):
    """Proxy for GitHub Actions input variables.

    Usage:
        class MyAction:
            @property
            def input(self):
                return InputProxy()

        action = MyAction()
        print(action.input["my-input"])
    """

    def __init__(self) -> None:
        self._input_keys: list[str] | None = None

    def __getitem__(self, name: str) -> str:
        # Do not use
        return os.environ[f"INPUT_{name.upper()}"]

    def __iter__(self) -> Iterator[str]:
        if self._input_keys is None:
            self._input_keys = [
                key[len(INPUT_PREFIX) :].lower()
                for key in os.environ
                if key.startswith(INPUT_PREFIX)
            ]
        return iter(self._input_keys)

    def __len__(self) -> int:
        return sum(1 for _ in self.__iter__())

    def __contains__(self, key: object) -> bool:
        assert isinstance(key, str)
        return f"{INPUT_PREFIX}{key.upper()}" in os.environ

    def __setitem__(self, name: str, value: str) -> None:
        raise ValueError("The input property is read-only.")

    def __delitem__(self, key: str) -> None:
        raise ValueError("The input property is read-only.")


class OutputProxy(MutableMapping[str, str]):
    """Proxy for GitHub Actions output variables.

    Usage:
        class MyAction:
            @property
            def output(self):
                return OutputProxy()

        action = MyAction()
        action.output["my-output"] = "value"
    """

    def __init__(self) -> None:
        self.output_file_path: Path = Path(os.environ["GITHUB_OUTPUT"])

    def __getitem__(self, key: str) -> str:
        return self._output_dict[key]

    def __setitem__(self, key: str, value: str) -> None:
        self._output_dict[key] = value
        self._save_output_file()

    def __delitem__(self, key: str) -> None:
        del self._output_dict[key]
        self._save_output_file()

    def __iter__(self) -> Iterator[str]:
        return iter(self._output_dict)

    def __len__(self) -> int:
        return len(self._output_dict)

    def __contains__(self, key: object) -> bool:
        return key in self._output_dict

    @cached_property
    def _output_dict(self) -> Dict[str, str]:
        """Load key-value pairs from a file, returning {} if the file does not exist."""
        try:
            content = self.output_file_path.read_text(encoding="utf-8")
            return dict(
                (line.split("=", 1) for line in content.splitlines() if "=" in line)
            )
        except FileNotFoundError:
            return {}

    def _save_output_file(self) -> None:
        self.output_file_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"{key}={value}" for key, value in self._output_dict.items()
        ]
        self.output_file_path.write_text("\n".join(lines), encoding="utf-8")

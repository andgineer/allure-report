"""Action base."""

from pathlib import Path

from .inputs_outputs import ActionOutputs, ActionInputs  # pylint: disable=relative-beyond-top-level


class ActionBase:
    """Base class for GitHub Actions."""

    @property
    def output(self) -> ActionOutputs:
        """Get Action Output."""
        return ActionOutputs()

    @property
    def input(self) -> ActionInputs:
        """Get Action Input."""
        return ActionInputs()

    def get_input_path(self, name: str) -> Path:
        """Get Action Input value as Path."""
        path_str = self.input[name]
        if not path_str:
            raise ValueError(f"Parameter `{name}` cannot be empty.")
        return Path(path_str)

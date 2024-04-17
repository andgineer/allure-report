"""Action base."""

import sys
import traceback
from pathlib import Path

from .github_vars import GithubVars  # pylint: disable=relative-beyond-top-level
from .inputs_outputs import ActionOutputs, ActionInputs  # pylint: disable=relative-beyond-top-level


class ActionBase:
    """Base class for GitHub Actions.

    Implement main() method in the subclass.
    """

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

    @property
    def vars(self) -> GithubVars:
        """Get GitHub Environment Variables."""
        return GithubVars()

    def main(self) -> None:
        """Main method."""
        raise NotImplementedError

    def run(self) -> None:
        """Run main method."""
        try:
            self.main()
        except Exception:  # pylint: disable=broad-except
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

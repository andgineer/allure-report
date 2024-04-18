"""Action base."""

import sys
import traceback
from typing import Any

from jinja2 import Template

from .github_vars import GithubVars  # pylint: disable=relative-beyond-top-level
from .inputs_outputs import ActionOutputs, ActionInputs  # pylint: disable=relative-beyond-top-level


class FileTextProperty:
    """Property descriptor read / write from a file."""

    def __init__(self, var_name: str) -> None:
        """Initialize the property descriptor.

        `var_name` is the name of the object's `vars` attribute with the path to the file.
        """
        self.var_name = var_name

    def __get__(self, obj: Any, objtype: Any = None) -> str:
        path = getattr(obj.vars, self.var_name)
        try:
            return path.read_text()  # type: ignore
        except FileNotFoundError:
            return ""

    def __set__(self, obj: Any, value: str) -> None:
        path = getattr(obj.vars, self.var_name)
        try:
            path.write_text(value)
        except FileNotFoundError:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)


class ActionBase:
    """Base class for GitHub Actions.

    Implement main() method in the subclass.
    """

    def __init__(self, inputs: ActionInputs = ActionInputs()):
        self.inputs = inputs
        self.outputs = ActionOutputs()
        self.vars = GithubVars()

    summary = FileTextProperty("github_step_summary")

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

    def render(self, template: str) -> str:
        """Render template with context including inputs, outputs, and vars."""
        return Template(template.replace("\\n", "\n")).render(
            vars=self.vars,
            inputs=self.inputs,
            outputs=self.outputs,
        )

"""Sable Commond Line Interface"""

from os import chdir
from pathlib import Path

from typer import Typer

from sable.load import load_file
from sable.view import view

app = Typer()


@app.command()
def run(path: str) -> None:
    """Run test cases.

    Switch to the same folder with the given test file, so that it can
    use the relevant path. Then run each test cases in the test file and
    print the results.

    Parameters
    ----------
    path : str
        The path of the test file, which can either be an absolute path
        or a relevant path.
    """
    filepath: Path = Path(path)
    chdir(filepath.parent)
    view(load_file(filepath.name))


def main() -> None:
    """Main function for CLI."""
    app()


if __name__ == "__main__":
    main()

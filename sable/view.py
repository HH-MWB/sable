"""Sable Viewer"""

from typing import Iterable

from typer import colors, echo, style

from sable.data import TestCase
from sable.exec import test

TAG_PASS: str = style("Passed", fg=colors.WHITE, bg=colors.GREEN)
TAG_FAIL: str = style("Failed", fg=colors.WHITE, bg=colors.RED)


def view(cases: Iterable[TestCase]) -> None:
    """View the results of given test cases.

    Parameters
    ----------
    cases : Iterable[TestCase]
        Test cases to be displayed
    """
    for case in cases:
        if test(case):
            echo(f"{case.identifier:.<73}{TAG_PASS}")
        else:
            echo(f"{case.identifier:.<73}{TAG_FAIL}\n\t{case.message}")

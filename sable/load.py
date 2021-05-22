"""Sable Loader"""

from io import StringIO
from pathlib import Path
from typing import Any, Dict, Tuple

from pandas import read_csv, read_fwf
from yaml import SafeLoader, YAMLObject, safe_load_all

from sable.data import Expectation, Query, Table, Tabulation, TestCase

###############################################################################
#                                YAML Objects                                 #
###############################################################################


class FileLoader(YAMLObject):
    """Load content from a file as a string."""

    yaml_tag = "!file"
    yaml_loader = SafeLoader

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.content = self.path.read_text()

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f"File({self.path})"

    @classmethod
    def from_yaml(cls, loader, node):
        return str(FileLoader(node.value))


class CsvParser(YAMLObject):
    """Convert CSV format string to a Tabulation."""

    yaml_tag = "!csv"
    yaml_loader = SafeLoader

    def __init__(self, string: str) -> None:
        dataframe = read_csv(StringIO(string))
        self.content = Tabulation(dataframe)

    def __str__(self) -> str:
        return self.content.dataframe.to_string()

    def __repr__(self) -> str:
        return str(self.content.dataframe.shape)

    @classmethod
    def from_yaml(cls, loader, node):
        return CsvParser(node.value).content


class FwfParser(YAMLObject):
    """Convert FWF format string to a Tabulation."""

    yaml_tag = "!fwf"
    yaml_loader = SafeLoader

    def __init__(self, string: str) -> None:
        dataframe = read_fwf(StringIO(string))
        self.content = Tabulation(dataframe)

    def __str__(self) -> str:
        return self.content.dataframe.to_string()

    def __repr__(self) -> str:
        return str(self.content.dataframe.shape)

    @classmethod
    def from_yaml(cls, loader, node):
        return FwfParser(node.value).content


###############################################################################
#                              Test Case Loader                               #
###############################################################################


def load_case(data: Dict[str, Any]) -> TestCase:
    """Load test case.

    Build a test case from data in the dictionary.

    Parameters
    ----------
    data : Dict[str, Any]
        The data for the test case.

    Returns
    -------
    TestCase
        Test case with given data.
    """
    query = Query(template=data["sql"], mapping=data.get("var", {}))

    table_name = data["exp"]["where"]
    if table_name == "result set":
        table_name = None
    expectation = Expectation(
        tabulation=data["exp"]["records"], table_name=table_name
    )

    environment = {
        Table(
            definition=table["metadata"],
            tabulation=table["records"],
        )
        for table in data.get("env", [])
    }

    return TestCase(
        query=query,
        expectation=expectation,
        environment=environment,
        identifier=data.get("uid"),
        message=data.get("msg"),
    )


###############################################################################
#                              Test File Loader                               #
###############################################################################


def load_file(path: str) -> Tuple[TestCase, ...]:
    """Load test cases from a file.

    Parameters
    ----------
    path : str
        File path.

    Returns
    -------
    Tuple[TestCase, ...]
        Test cases.
    """
    with open(path, "r") as file:
        return tuple(
            load_case(case)
            for data in safe_load_all(file.read())
            if data.get("version") == "v0.1"
            for case in data.get("cases", [])
        )

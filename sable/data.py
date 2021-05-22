"""Sable Data Classes"""

from dataclasses import dataclass, field
from string import Template
from typing import Any, Dict, Optional, Set, Tuple

from ddlparse import DdlParse
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from tabulate import tabulate


@dataclass(frozen=True)
class Tabulation:
    """Tabulation

    Tabulation is a data structure that contains data in a table-like
    structure. It has rows and columns, and each column got a name.

    Attributes
    ----------
    dataframe : DataFrame
        Stores the data and column names.
    columns : Tuple[str, ...]
        Name for each columns.
    """

    dataframe: DataFrame

    @property
    def columns(self) -> Tuple[str, ...]:
        return tuple(str(col) for col in self.dataframe.columns)

    def __str__(self) -> str:
        return str(tabulate(self.dataframe, headers="keys", tablefmt="psql"))

    def __repr__(self) -> str:
        rows, cols = self.dataframe.shape
        return f"Tabulation(num_of_rows={rows}, num_of_cols={cols})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Tabulation):
            return False

        try:
            assert_frame_equal(self.dataframe, other.dataframe)
        except AssertionError:
            return False
        else:
            return True


@dataclass(frozen=True)
class Table:
    """Table

    A table in the database, which contains the table definition and data.

    Attributes
    ----------
    definition : str
        The data definition language (DDL) of this table.
    tabulation : Tabulation
        The data of this table.
    name : str
        Table name.
    database : str
        The database this table belongs to.
    """

    definition: str
    tabulation: Tabulation
    name: str = field(init=False)
    database: str = field(init=False)

    def __post_init__(self) -> None:
        # parse definition query
        ddl = DdlParse().parse(self.definition)

        # verification
        def_cols = {col.name for col in ddl.columns.values()}
        tab_cols = set(self.tabulation.columns)
        assert def_cols == tab_cols

        # assign parsed result
        object.__setattr__(self, "name", ddl.name)
        object.__setattr__(self, "database", ddl.schema)

    def __hash__(self) -> int:
        return hash((self.database, self.name))

    def __str__(self) -> str:
        return (
            f"{self.database}.{self.name}"
            if self.database != ""
            else self.name
        )

    def __repr__(self) -> str:
        return f"Table('{str(self)}')"


@dataclass(frozen=True)
class Query:
    """Query

    SQL query, which contains a query template and a dictionary be used
    to format the template.

    Attributes
    ----------
    template : str
        A string template will be formatted to generate the query.
    mapping : Dict[str, str]
        Dictionary to be used to format the template.
    """

    template: str
    mapping: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        return Template(self.template).safe_substitute(self.mapping)


@dataclass(frozen=True)
class Expectation:
    """Expectation

    The expected result for a test case, which contains the table needs
    to be inspected (or the result set) and the expected data in it.

    Attributes
    ----------
    tabulation : Tabulation
        Expected data.
    table_name : str or None
        Name of table to be inspected. None means the result set.
    """

    tabulation: Tabulation
    table_name: Optional[str] = None

    def expect_checking_from_result(self) -> bool:
        """Expect checking from result."""
        return self.table_name is None


@dataclass(frozen=True)
class TestCase:
    """Test Case

    The test case, which is a specification of the database environment,
    execution query, execution conditions, expected results, and basic
    testing information.

    Attributes
    ----------
    query : Query
        The SQL query to be tested.
    expectation : Expectation
        The expected result.
    environment : Set[Table]
        The mocked database environment, like pre-defined tables & data.
    identifier : str or None
        An identifier for this test case.
    message : str
        The message has been displayed when the case got an error or
        failed.
    """

    query: Query
    expectation: Expectation
    environment: Set[Table] = field(default_factory=set)
    identifier: Optional[str] = None
    message: Optional[str] = None

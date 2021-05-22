"""Sable Executor"""

from contextlib import contextmanager
from sqlite3 import Connection, connect
from typing import Iterable, Iterator

from pandas import read_sql_query

from sable.data import Table, Tabulation, TestCase


@contextmanager
def create_sqlite() -> Iterator[Connection]:
    """Create SQLite connection.

    Create an SQLite connection that can be used for running test cases.

    Yields
    -------
    Iterator[Connection]
        Connection to a newly created SQLite database.
    """
    connection = connect(":memory:")
    try:
        yield connection
    finally:
        connection.close()


def setup_environ(
    connection: Connection, environment: Iterable[Table]
) -> None:
    """Set up environment.

    Given an expected environment, which contains the tables and data,
    set up the database to match the expected environment through given
    connection.

    Parameters
    ----------
    connection : Connection
        A connection to the database will be set in the environment.
    environment : Iterable[Table]
        Expected environment, which contains tables and data.
    """
    cursor = connection.cursor()
    for table in environment:
        cursor.execute(table.definition)
        table.tabulation.dataframe.to_sql(
            table.name,
            connection,
            if_exists="append",
            index=False,
        )


def test(case: TestCase) -> bool:
    """Run a test case and get pass/fail result.

    Parameters
    ----------
    case : TestCase
        The test case to be checked.

    Returns
    -------
    bool
        True for a pass and false for a fail.
    """
    with create_sqlite() as connection:
        setup_environ(connection, case.environment)

        if case.expectation.expect_checking_from_result():
            captured_frame = read_sql_query(str(case.query), connection)
        else:
            cursor = connection.cursor()
            cursor.execute(str(case.query))
            captured_frame = read_sql_query(
                f"SELECT * FROM {case.expectation.table_name};", connection
            )

    return Tabulation(captured_frame) == case.expectation.tabulation

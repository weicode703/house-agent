from types import SimpleNamespace

import pytest
from sqlalchemy.exc import OperationalError

from src.db_retry import invoke_database_tool_with_retry


def test_database_tool_retries_mysql_disconnect(monkeypatch) -> None:
    calls = 0

    def invoke(_tool_input):
        nonlocal calls
        calls += 1
        if calls < 3:
            raise OperationalError("SELECT 1", {}, RuntimeError(2006, "server has gone away"))
        return "schema"

    monkeypatch.setattr("src.db_retry.time.sleep", lambda _: None)
    tool = SimpleNamespace(name="sql_db_schema", invoke=invoke)

    assert invoke_database_tool_with_retry(tool, {"table_names": "house"}) == "schema"
    assert calls == 3


def test_database_tool_does_not_retry_non_disconnect_error(monkeypatch) -> None:
    calls = 0

    def invoke(_tool_input):
        nonlocal calls
        calls += 1
        raise OperationalError("SELECT 1", {}, RuntimeError(1064, "syntax error"))

    monkeypatch.setattr("src.db_retry.time.sleep", lambda _: None)
    tool = SimpleNamespace(name="sql_db_schema", invoke=invoke)

    with pytest.raises(OperationalError):
        invoke_database_tool_with_retry(tool, {"table_names": "house"})

    assert calls == 1

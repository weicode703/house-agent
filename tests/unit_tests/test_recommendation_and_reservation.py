from langchain_core.messages import AIMessage, HumanMessage

from agent.node.main import need_reserve
from agent.node.recommend import _enforce_query_limit, _normalize_room_count
from agent.node.reserve import _title_exists_in_history


def test_recommendation_count_defaults_and_is_bounded() -> None:
    assert _normalize_room_count(None) == 5
    assert _normalize_room_count(0) == 5
    assert _normalize_room_count(-2) == 5
    assert _normalize_room_count(50) == 20


def test_query_limit_is_positive_and_replaced() -> None:
    assert _enforce_query_limit("SELECT * FROM house", 5) == "SELECT * FROM house LIMIT 5"
    assert _enforce_query_limit("SELECT * FROM house LIMIT 0;", 5) == "SELECT * FROM house LIMIT 5"
    assert _enforce_query_limit("SELECT * FROM house LIMIT 10 OFFSET 3", 4) == (
        "SELECT * FROM house LIMIT 4"
    )


def test_reservation_title_must_be_shown_by_assistant() -> None:
    title = "整租·张各庄村东1号楼"
    assert not _title_exists_in_history(
        {"messages": [HumanMessage(content=title)]},
        title,
    )
    assert _title_exists_in_history(
        {"messages": [AIMessage(content=f"推荐房源：{title}")]},
        title,
    )


def test_reservation_accepts_selected_title_at_confirmation(monkeypatch) -> None:
    title = "整租·葫芦垡新村 1室1厅1卫"
    monkeypatch.setattr("agent.node.main.interrupt", lambda _: title)

    assert need_reserve({}) == {"reserve": "需要", "title": title}


def test_reservation_decline_does_not_start_reservation(monkeypatch) -> None:
    monkeypatch.setattr("agent.node.main.interrupt", lambda _: "不需要")

    assert need_reserve({}) == {"reserve": "不需要", "title": ""}

"""Tests for Epic 2: inter-agent messaging."""

from __future__ import annotations

import pytest

from agents.messaging import AgentMessage, MessageBus, MessagePriority


@pytest.fixture()
def bus() -> MessageBus:
    return MessageBus()


# ---------------------------------------------------------------------------
# Basic publish/subscribe
# ---------------------------------------------------------------------------


def test_publish_to_subscriber(bus: MessageBus) -> None:
    received: list[AgentMessage] = []
    bus.subscribe("reviewer", lambda msg: received.append(msg))
    msg = AgentMessage(
        sender="architect", recipient="reviewer", subject="review_request"
    )
    count = bus.publish(msg)
    assert count == 1
    assert len(received) == 1
    assert received[0].subject == "review_request"


def test_wildcard_subscriber_receives_all(bus: MessageBus) -> None:
    received: list[AgentMessage] = []
    bus.subscribe("*", lambda msg: received.append(msg))
    bus.publish(AgentMessage(sender="a", recipient="b", subject="s1"))
    bus.publish(AgentMessage(sender="c", recipient="d", subject="s2"))
    assert len(received) == 2


def test_no_subscriber_returns_zero(bus: MessageBus) -> None:
    msg = AgentMessage(sender="x", recipient="y", subject="test")
    assert bus.publish(msg) == 0


def test_unsubscribe_stops_delivery(bus: MessageBus) -> None:
    received: list[AgentMessage] = []

    def handler(msg: AgentMessage) -> None:
        received.append(msg)

    bus.subscribe("agent-a", handler)
    bus.publish(AgentMessage(sender="x", recipient="agent-a", subject="first"))
    bus.unsubscribe("agent-a", handler)
    bus.publish(AgentMessage(sender="x", recipient="agent-a", subject="second"))
    assert len(received) == 1


# ---------------------------------------------------------------------------
# Message properties
# ---------------------------------------------------------------------------


def test_message_has_unique_id() -> None:
    m1 = AgentMessage(sender="a", recipient="b", subject="s")
    m2 = AgentMessage(sender="a", recipient="b", subject="s")
    assert m1.message_id != m2.message_id


def test_message_default_priority() -> None:
    msg = AgentMessage(sender="a", recipient="b", subject="s")
    assert msg.priority == MessagePriority.NORMAL


def test_message_payload() -> None:
    msg = AgentMessage(
        sender="a", recipient="b", subject="handoff", payload={"artifact_id": "req-1"}
    )
    assert msg.payload["artifact_id"] == "req-1"


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def test_history_records_all_messages(bus: MessageBus) -> None:
    bus.publish(AgentMessage(sender="a", recipient="b", subject="s1"))
    bus.publish(AgentMessage(sender="c", recipient="d", subject="s2"))
    assert len(bus.history()) == 2


def test_history_filter_by_sender(bus: MessageBus) -> None:
    bus.publish(AgentMessage(sender="alice", recipient="bob", subject="s"))
    bus.publish(AgentMessage(sender="carol", recipient="bob", subject="s"))
    assert len(bus.history(sender="alice")) == 1


def test_history_filter_by_recipient(bus: MessageBus) -> None:
    bus.publish(AgentMessage(sender="a", recipient="bob", subject="s"))
    bus.publish(AgentMessage(sender="a", recipient="carol", subject="s"))
    assert len(bus.history(recipient="bob")) == 1


def test_clear_history(bus: MessageBus) -> None:
    bus.publish(AgentMessage(sender="a", recipient="b", subject="s"))
    bus.clear_history()
    assert bus.history() == []

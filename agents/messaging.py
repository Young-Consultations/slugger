"""Inter-agent messaging and artifact passing.

Provides a lightweight in-process message bus that allows agents to publish
and subscribe to typed messages, enabling loosely-coupled collaboration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4


class MessagePriority(str, Enum):
    """Priority levels for agent messages."""

    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    CRITICAL = 'critical'


@dataclass(slots=True)
class AgentMessage:
    """A message passed between agents.

    Parameters
    ----------
    sender:
        Name of the sending agent.
    recipient:
        Name of the target agent, or ``'*'`` for broadcast.
    subject:
        Short description of the message purpose.
    payload:
        Arbitrary message content.
    message_id:
        Auto-generated UUID for tracing.
    priority:
        Delivery priority.
    correlation_id:
        Optional ID linking this message to a workflow run or prior message.
    timestamp:
        UTC timestamp of creation.
    """

    sender: str
    recipient: str
    subject: str
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: str(uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


MessageHandler = Callable[[AgentMessage], None]


class MessageBus:
    """In-process publish/subscribe message bus for agent collaboration.

    Agents register handlers by agent name or use the wildcard ``'*'`` to
    receive all messages.

    Examples
    --------
    >>> bus = MessageBus()
    >>> received = []
    >>> bus.subscribe('reviewer', lambda msg: received.append(msg))
    >>> bus.publish(AgentMessage(sender='architect', recipient='reviewer', subject='review_request'))
    >>> len(received)
    1
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._history: list[AgentMessage] = []

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(self, agent_name: str, handler: MessageHandler) -> None:
        """Register *handler* for messages sent to *agent_name*.

        Use ``'*'`` to subscribe to all messages.
        """
        self._handlers.setdefault(agent_name, []).append(handler)

    def unsubscribe(self, agent_name: str, handler: MessageHandler) -> None:
        """Remove a previously registered *handler*."""
        handlers = self._handlers.get(agent_name, [])
        if handler in handlers:
            handlers.remove(handler)

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    def publish(self, message: AgentMessage) -> int:
        """Deliver *message* to the appropriate subscribers.

        Dispatches to handlers registered for the specific recipient and to
        wildcard (``'*'``) handlers.

        Returns
        -------
        int
            Number of handlers invoked.
        """
        self._history.append(message)
        dispatched = 0
        if message.recipient == '*':
            for handlers in list(self._handlers.values()):
                for handler in list(handlers):
                    handler(message)
                    dispatched += 1
        else:
            for handler in list(self._handlers.get(message.recipient, [])):
                handler(message)
                dispatched += 1
            for handler in list(self._handlers.get('*', [])):
                handler(message)
                dispatched += 1
        return dispatched

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def history(self, *, sender: str | None = None, recipient: str | None = None) -> list[AgentMessage]:
        """Return message history, optionally filtered by sender or recipient."""
        messages = self._history
        if sender is not None:
            messages = [m for m in messages if m.sender == sender]
        if recipient is not None:
            messages = [m for m in messages if m.recipient == recipient]
        return list(messages)

    def clear_history(self) -> None:
        """Remove all recorded messages from history."""
        self._history.clear()

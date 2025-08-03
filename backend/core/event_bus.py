"""
BrainSAIT Healthcare Platform - Event Bus
Provides a pubsub-style event system for component communication.

This module implements an asynchronous event bus system that allows different
parts of the application to communicate through a standardized interface.
"""

import logging
import asyncio
import uuid
from typing import Any, Dict, List, Callable, Awaitable, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class EventBus:
    """
    Asynchronous event bus for application-wide event handling

    This class provides a publish-subscribe pattern for event distribution
    across the healthcare platform components.
    """

    def __init__(self):
        """Initialize event bus with empty subscribers"""
        self.subscribers: Dict[str, Dict[str, Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000  # Maximum events to keep in history

    async def publish(self, event_type: str, data: Any, retain: bool = False) -> str:
        """
        Publish an event to all subscribers of the given event type

        Args:
            event_type: The type of event to publish
            data: The data payload for the event
            retain: Whether to retain event in history

        Returns:
            event_id: Unique ID for the published event
        """
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        if retain:
            self.event_history.append(event)
            # Trim history if needed
            if len(self.event_history) > self.max_history:
                self.event_history = self.event_history[-self.max_history:]

        # Notify all subscribers
        if event_type in self.subscribers:
            subscribers = list(self.subscribers[event_type].items())

            # Create tasks for all subscribers
            tasks = []
            for sub_id, callback in subscribers:
                try:
                    task = asyncio.create_task(
                        self._call_subscriber(callback, event)
                    )
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Error creating task for subscriber {sub_id}: {e}")

            # Wait for all subscribers to process the event
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        return event_id

    async def _call_subscriber(
        self,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        event: Dict[str, Any]
    ) -> None:
        """Call a subscriber with error handling"""
        try:
            await callback(event)
        except Exception as e:
            logger.error(f"Error in event subscriber: {e}")

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> str:
        """
        Subscribe to an event type

        Args:
            event_type: The event type to subscribe to
            callback: Async function to call when event occurs

        Returns:
            subscription_id: ID to use for unsubscribing
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = {}

        subscription_id = str(uuid.uuid4())
        self.subscribers[event_type][subscription_id] = callback
        return subscription_id

    def unsubscribe(self, event_type: str, subscription_id: str) -> bool:
        """Unsubscribe from an event type using subscription ID"""
        if (event_type in self.subscribers and
                subscription_id in self.subscribers[event_type]):
            del self.subscribers[event_type][subscription_id]

            # Clean up empty event types
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]

            return True
        return False

    def get_event_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent events, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self.event_history if e["type"] == event_type]
            return filtered[-limit:]
        return self.event_history[-limit:]


# Default event bus instance
event_bus = EventBus()

# Healthcare-specific event types
class HealthcareEventTypes:
    """Standard event types for healthcare platform events"""

    # Identity events
    IDENTITY_CREATED = "healthcare.identity.created"
    IDENTITY_UPDATED = "healthcare.identity.updated"
    IDENTITY_REVOKED = "healthcare.identity.revoked"

    # NPHIES events
    CLAIM_SUBMITTED = "nphies.claim.submitted"
    CLAIM_UPDATED = "nphies.claim.updated"
    CLAIM_RESPONSE = "nphies.claim.response"

    # AI analytics events
    ANALYSIS_REQUESTED = "ai.analysis.requested"
    ANALYSIS_COMPLETED = "ai.analysis.completed"

    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    ERROR_OCCURRED = "system.error"

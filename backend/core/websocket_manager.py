"""
BrainSAIT Healthcare Platform - WebSocket Manager
Provides real-time communication capabilities for the platform.

This module implements a WebSocket manager that handles real-time
communication between the server and clients, with support for
channels, authentication, and message routing.
"""

import logging
import json
from typing import Dict, List, Set, Any, Optional, Callable
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, status

# Configure logging
logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    WebSocket connection manager with support for channels and authentication

    This class provides functionality for:
    - Managing WebSocket connections
    - Authentication
    - Channel-based subscriptions
    - Broadcasting messages
    """

    def __init__(self):
        """Initialize connection manager with empty connections"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.channels: Dict[str, Set[str]] = {}
        self.user_channels: Dict[str, Set[str]] = {}
        self.auth_handlers: Dict[str, Callable] = {}

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        token: Optional[str] = None
    ) -> bool:
        """
        Accept a WebSocket connection with optional authentication

        Args:
            websocket: The WebSocket connection
            client_id: Unique identifier for the client
            token: Optional authentication token

        Returns:
            bool: Connection success
        """
        try:
            # Authenticate if token is provided and handler exists
            if token and 'default' in self.auth_handlers:
                is_authenticated = await self.auth_handlers['default'](token)
                if not is_authenticated:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return False

            # Accept the connection
            await websocket.accept()

            # Register the connection
            self.active_connections[client_id] = websocket
            self.user_channels[client_id] = set()

            # Send welcome message
            await self.send_personal_message(
                {"type": "system", "message": "Connected to BrainSAIT Healthcare Platform"},
                client_id
            )

            logger.info(f"Client {client_id} connected")
            return True

        except Exception as e:
            logger.error(f"Error connecting client {client_id}: {e}")
            return False

    def disconnect(self, client_id: str):
        """
        Handle client disconnection

        Args:
            client_id: ID of the client to disconnect
        """
        # Remove from all subscribed channels
        if client_id in self.user_channels:
            channels = list(self.user_channels[client_id])
            for channel in channels:
                self.unsubscribe(client_id, channel)
            del self.user_channels[client_id]

        # Remove from active connections
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        logger.info(f"Client {client_id} disconnected")

    def subscribe(self, client_id: str, channel: str) -> bool:
        """
        Subscribe a client to a channel

        Args:
            client_id: Client ID to subscribe
            channel: Channel name to subscribe to

        Returns:
            bool: Subscription success
        """
        if client_id not in self.active_connections:
            return False

        # Initialize channel if it doesn't exist
        if channel not in self.channels:
            self.channels[channel] = set()

        # Add client to channel
        self.channels[channel].add(client_id)

        # Track channel in user's subscriptions
        if client_id not in self.user_channels:
            self.user_channels[client_id] = set()
        self.user_channels[client_id].add(channel)

        logger.info(f"Client {client_id} subscribed to channel {channel}")
        return True

    def unsubscribe(self, client_id: str, channel: str) -> bool:
        """
        Unsubscribe a client from a channel

        Args:
            client_id: Client ID to unsubscribe
            channel: Channel to unsubscribe from

        Returns:
            bool: Unsubscription success
        """
        # Remove from channel
        if channel in self.channels and client_id in self.channels[channel]:
            self.channels[channel].remove(client_id)

            # Clean up empty channels
            if not self.channels[channel]:
                del self.channels[channel]

            # Remove from user's subscriptions
            if client_id in self.user_channels:
                self.user_channels[client_id].discard(channel)

            logger.info(f"Client {client_id} unsubscribed from channel {channel}")
            return True

        return False

    async def broadcast_to_channel(self, message: Any, channel: str):
        """
        Broadcast a message to all clients in a channel

        Args:
            message: Message to broadcast
            channel: Channel to broadcast to
        """
        if channel not in self.channels:
            return

        disconnected = []
        json_message = self._prepare_message(message)

        # Send to all clients in the channel
        for client_id in self.channels[channel]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_text(json_message)
                except WebSocketDisconnect:
                    disconnected.append(client_id)
                except Exception as e:
                    logger.error(f"Error sending to client {client_id}: {e}")
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast(self, message: Any):
        """Broadcast a message to all connected clients"""
        disconnected = []
        json_message = self._prepare_message(message)

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json_message)
            except WebSocketDisconnect:
                disconnected.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_personal_message(self, message: Any, client_id: str) -> bool:
        """
        Send a message to a specific client

        Args:
            message: Message to send
            client_id: Target client ID

        Returns:
            bool: Message sent successfully
        """
        if client_id not in self.active_connections:
            return False

        try:
            json_message = self._prepare_message(message)
            await self.active_connections[client_id].send_text(json_message)
            return True
        except WebSocketDisconnect:
            self.disconnect(client_id)
            return False
        except Exception as e:
            logger.error(f"Error sending personal message to {client_id}: {e}")
            return False

    def _prepare_message(self, message: Any) -> str:
        """
        Prepare message for sending

        Converts message to JSON string if it's not already a string
        """
        if isinstance(message, str):
            return message

        # Add timestamp if it's a dict without one
        if isinstance(message, dict) and "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        return json.dumps(message)

    def register_auth_handler(
        self,
        handler_name: str,
        handler: Callable[[str], bool]
    ):
        """Register an authentication handler function"""
        self.auth_handlers[handler_name] = handler

    def get_channel_count(self, channel: str) -> int:
        """Get number of clients in a channel"""
        if channel not in self.channels:
            return 0
        return len(self.channels[channel])

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)


# Default WebSocket manager instance
websocket_manager = WebSocketManager()

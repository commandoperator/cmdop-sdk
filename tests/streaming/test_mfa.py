"""
Tests for TerminalStream MFA AuthChallenge handling.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

from cmdop.streaming.terminal import TerminalStream


class TestHandleAuthChallenge:
    """Test _handle_auth_challenge() method."""

    async def test_reads_totp_from_env(self):
        """Reads TOTP code from CMDOP_TOTP_CODE env var and sends auth response."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "sess-env"

        challenge = MagicMock()
        challenge.challenge_id = "chal-env-1"
        challenge.methods = ["totp"]

        with patch.dict(os.environ, {"CMDOP_TOTP_CODE": "123456"}):
            with patch.object(stream, "_send_auth_response", new_callable=AsyncMock) as mock_send:
                await stream._handle_auth_challenge(challenge)

        mock_send.assert_awaited_once_with("chal-env-1", "123456")

    async def test_prompts_stdin_when_no_env(self):
        """Prompts via stdin when env var is absent, then sends auth response."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "sess-stdin"

        challenge = MagicMock()
        challenge.challenge_id = "chal-stdin-1"
        challenge.methods = ["totp"]

        # Remove CMDOP_TOTP_CODE from env if present, then mock the executor prompt
        env_without_totp = {k: v for k, v in os.environ.items() if k != "CMDOP_TOTP_CODE"}
        with patch.dict(os.environ, env_without_totp, clear=True):
            with patch("cmdop.streaming.terminal.asyncio.get_event_loop") as mock_get_loop:
                mock_loop = MagicMock()
                mock_loop.run_in_executor = AsyncMock(return_value="654321")
                mock_get_loop.return_value = mock_loop

                with patch.object(stream, "_send_auth_response", new_callable=AsyncMock) as mock_send:
                    await stream._handle_auth_challenge(challenge)

        mock_send.assert_awaited_once_with("chal-stdin-1", "654321")

    async def test_does_nothing_when_no_code(self):
        """Does not call _send_auth_response when both env and stdin return empty string."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "sess-nocode"

        challenge = MagicMock()
        challenge.challenge_id = "chal-nocode-1"
        challenge.methods = ["totp"]

        env_without_totp = {k: v for k, v in os.environ.items() if k != "CMDOP_TOTP_CODE"}
        with patch.dict(os.environ, env_without_totp, clear=True):
            with patch("cmdop.streaming.terminal.asyncio.get_event_loop") as mock_get_loop:
                mock_loop = MagicMock()
                mock_loop.run_in_executor = AsyncMock(return_value="")
                mock_get_loop.return_value = mock_loop

                with patch.object(stream, "_send_auth_response", new_callable=AsyncMock) as mock_send:
                    await stream._handle_auth_challenge(challenge)

        mock_send.assert_not_awaited()


class TestSendAuthResponse:
    """Test _send_auth_response() method."""

    async def test_enqueues_agent_message_with_auth_response(self):
        """Enqueues AgentMessage with correct challenge_id and totp_code."""
        transport = MagicMock()
        stream = TerminalStream(transport)
        stream._session_id = "sess-1"
        stream._queue = asyncio.Queue()

        await stream._send_auth_response("chal-1", "123456")

        assert not stream._queue.empty()
        msg = stream._queue.get_nowait()

        assert msg.session_id == "sess-1"
        assert msg.auth_response.challenge_id == "chal-1"
        assert msg.auth_response.totp_code == "123456"


class TestAuthChallengeIntegration:
    """Integration tests for auth_challenge dispatch via _handle_message."""

    async def test_handle_message_dispatches_auth_challenge(self):
        """_handle_message schedules _handle_auth_challenge via ensure_future for auth_challenge payload."""
        transport = MagicMock()
        stream = TerminalStream(transport)

        auth_challenge = MagicMock()
        auth_challenge.challenge_id = "c1"
        auth_challenge.methods = ["totp"]

        msg = MagicMock()
        msg.WhichOneof.return_value = "auth_challenge"
        msg.auth_challenge = auth_challenge

        captured_coros = []

        def capture_ensure_future(coro):
            captured_coros.append(coro)
            # Await the coroutine immediately so Pyright doesn't warn about unused coroutine
            loop = asyncio.get_event_loop()
            future = loop.create_task(coro)
            return future

        with patch.object(stream, "_handle_auth_challenge", new_callable=AsyncMock) as mock_handler:
            with patch("cmdop.streaming.terminal.asyncio.ensure_future", side_effect=capture_ensure_future):
                await stream._handle_message(msg)

        assert len(captured_coros) == 1
        mock_handler.assert_called_once_with(auth_challenge)

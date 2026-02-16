"""
Tests for CLI module.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from cmdop.cli import main


class TestCLIMain:
    """Test main CLI group."""

    def test_help(self):
        """--help shows usage."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "CMDOP SDK" in result.output

    def test_version(self):
        """--version shows version."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output


class TestCLISSH:
    """Test ssh command."""

    def test_ssh_help(self):
        """ssh --help shows usage."""
        runner = CliRunner()
        result = runner.invoke(main, ["ssh", "--help"])
        assert result.exit_code == 0
        assert "SSH-like" in result.output

    def test_ssh_no_api_key(self):
        """ssh fails without API key."""
        runner = CliRunner()
        result = runner.invoke(main, ["ssh", "my-server"], env={"CMDOP_API_KEY": ""})
        assert result.exit_code == 1
        assert "CMDOP_API_KEY" in result.output


class TestCLIFleet:
    """Test fleet command."""

    def test_fleet_help(self):
        """fleet --help shows usage."""
        runner = CliRunner()
        result = runner.invoke(main, ["fleet", "--help"])
        assert result.exit_code == 0
        assert "Fleet" in result.output

    def test_fleet_status_help(self):
        """fleet status --help shows usage."""
        runner = CliRunner()
        result = runner.invoke(main, ["fleet", "status", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_fleet_status_no_api_key(self):
        """fleet status fails without API key."""
        runner = CliRunner()
        result = runner.invoke(main, ["fleet", "status"], env={"CMDOP_API_KEY": ""})
        assert result.exit_code == 1
        assert "CMDOP_API_KEY" in result.output


class TestCLIExec:
    """Test exec command."""

    def test_exec_help(self):
        """exec --help shows usage."""
        runner = CliRunner()
        result = runner.invoke(main, ["exec", "--help"])
        assert result.exit_code == 0
        assert "Execute" in result.output

    def test_exec_no_api_key(self):
        """exec fails without API key."""
        runner = CliRunner()
        result = runner.invoke(
            main, ["exec", "my-server", "ls"], env={"CMDOP_API_KEY": ""}
        )
        assert result.exit_code == 1
        assert "CMDOP_API_KEY" in result.output


class TestCLITUI:
    """Test tui command."""

    def test_tui_help(self):
        """tui --help shows usage."""
        runner = CliRunner()
        result = runner.invoke(main, ["tui", "--help"])
        assert result.exit_code == 0
        assert "TUI" in result.output

    def test_tui_no_api_key(self):
        """tui fails without API key."""
        runner = CliRunner()
        result = runner.invoke(main, ["tui"], env={"CMDOP_API_KEY": ""})
        assert result.exit_code == 1
        assert "CMDOP_API_KEY" in result.output

"""Tests for browser extraction methods."""

from unittest.mock import MagicMock

import pytest

from cmdop.services.browser import BrowserService

from .conftest import MockTransport


class TestBrowserServiceExtract:
    """Test BrowserService.extract method."""

    def test_extract_text(self):
        """Test extracting text from elements."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.values = ["Item 1", "Item 2", "Item 3"]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtract = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract("session-123", ".item")

        assert result == ["Item 1", "Item 2", "Item 3"]

    def test_extract_attribute(self):
        """Test extracting attribute from elements."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.values = ["/link1", "/link2"]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtract = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract("session-123", "a", attr="href")

        assert result == ["/link1", "/link2"]

    def test_extract_with_limit(self):
        """Test extracting with limit."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.values = ["Item 1"]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtract = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract("session-123", ".item", limit=1)

        assert len(result) == 1


class TestBrowserServiceExtractRegex:
    """Test BrowserService.extract_regex method."""

    def test_extract_regex(self):
        """Test extracting with regex."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.matches = ["test@example.com", "user@test.com"]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtractRegex = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract_regex("session-123", r"[\w.-]+@[\w.-]+\.\w+")

        assert result == ["test@example.com", "user@test.com"]

    def test_extract_regex_from_html(self):
        """Test extracting regex from HTML source."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.matches = ["<div>content</div>"]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtractRegex = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract_regex("session-123", r"<div>.*?</div>", from_html=True)

        assert len(result) == 1


class TestBrowserServiceValidateSelectors:
    """Test BrowserService.validate_selectors method."""

    def test_validate_selectors_success(self):
        """Test successful selector validation."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.valid = True
        mock_response.counts = {"title": 10, "price": 10}
        mock_response.samples = {"title": "Product 1", "price": "$99"}
        mock_response.errors = []
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserValidateSelectors = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.validate_selectors(
            "session-123",
            item=".product-card",
            fields={"title": ".title", "price": ".price"}
        )

        assert result["valid"] is True
        assert result["counts"]["title"] == 10
        assert result["samples"]["title"] == "Product 1"
        assert result["errors"] == []

    def test_validate_selectors_invalid(self):
        """Test validation with invalid selectors."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.valid = False
        mock_response.counts = {"title": 0, "price": 5}
        mock_response.samples = {"title": "", "price": "$99"}
        mock_response.errors = ["title: no elements found"]
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserValidateSelectors = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.validate_selectors(
            "session-123",
            item=".product-card",
            fields={"title": ".title", "price": ".price"}
        )

        assert result["valid"] is False
        assert result["counts"]["title"] == 0
        assert "title: no elements found" in result["errors"]

    def test_validate_selectors_failure(self):
        """Test validation with gRPC error."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error = "browser session not found"

        mock_stub = MagicMock()
        mock_stub.BrowserValidateSelectors = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with pytest.raises(RuntimeError, match="browser session not found"):
            service.validate_selectors(
                "session-123",
                item=".product",
                fields={"title": ".title"}
            )


class TestBrowserServiceExtractData:
    """Test BrowserService.extract_data method."""

    def test_extract_data_success(self):
        """Test successful data extraction."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.items_json = '[{"title": "Product 1", "price": "99"}, {"title": "Product 2", "price": "149"}]'
        mock_response.count = 2
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtractData = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract_data(
            "session-123",
            item=".product-card",
            fields_json='{"title": ".title", "price": ".price"}',
            limit=100
        )

        assert result["count"] == 2
        assert len(result["items"]) == 2
        assert result["items"][0]["title"] == "Product 1"
        assert result["items"][1]["price"] == "149"

    def test_extract_data_empty(self):
        """Test extraction with no results."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.items_json = ""
        mock_response.count = 0
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtractData = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract_data(
            "session-123",
            item=".product-card",
            fields_json='{"title": ".title"}'
        )

        assert result["count"] == 0
        assert result["items"] == []

    def test_extract_data_with_limit(self):
        """Test extraction with custom limit."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.items_json = '[{"title": "Item 1"}]'
        mock_response.count = 1
        mock_response.error = ""

        mock_stub = MagicMock()
        mock_stub.BrowserExtractData = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        result = service.extract_data(
            "session-123",
            item=".item",
            fields_json='{"title": ".title"}',
            limit=1
        )

        assert result["count"] == 1
        mock_stub.BrowserExtractData.assert_called_once()

    def test_extract_data_failure(self):
        """Test extraction with gRPC error."""
        transport = MockTransport()
        service = BrowserService(transport)

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error = "invalid selector syntax"

        mock_stub = MagicMock()
        mock_stub.BrowserExtractData = MagicMock(return_value=mock_response)
        service._stub = mock_stub

        with pytest.raises(RuntimeError, match="invalid selector syntax"):
            service.extract_data(
                "session-123",
                item=".product",
                fields_json='{"title": "invalid[["}'
            )

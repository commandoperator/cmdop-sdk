"""DOM capability."""

from __future__ import annotations
from typing import TYPE_CHECKING

from cmdop.services.browser.js import build_select_js, build_close_modal_js
from cmdop.services.browser.parsing import parse_html, SoupWrapper

from ._base import BaseCapability
from ._helpers import to_dict

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class DOMCapability(BaseCapability):
    """DOM operations: extraction, forms, modals.

    Usage:
        html = session.dom.html()
        soup = session.dom.soup()
        session.dom.select("#country", value="US")
    """

    def html(self, selector: str | None = None) -> str:
        """Get page HTML."""
        return self._call("get_html", selector)

    def text(self, selector: str | None = None) -> str:
        """Get page text content."""
        return self._call("get_text", selector)

    def soup(self, selector: str | None = None) -> SoupWrapper:
        """Get HTML as SoupWrapper with chainable API."""
        return SoupWrapper(html=self.html(selector))

    def parse(self, html: str | None = None, selector: str | None = None) -> "BeautifulSoup":
        """Parse HTML with BeautifulSoup."""
        if html is None:
            html = self.html(selector)
        return parse_html(html)

    def select(
        self,
        selector: str,
        value: str | None = None,
        text: str | None = None,
    ) -> dict:
        """Select dropdown option by value or text."""
        js = build_select_js(selector, value, text)
        return to_dict(self._js(js))

    def close_modal(self, selectors: list[str] | None = None) -> bool:
        """Try to close modal/dialog."""
        js = build_close_modal_js(selectors)
        return to_dict(self._js(js)).get("success", False)

    def extract(
        self, selector: str, attr: str | None = None, limit: int = 100
    ) -> list[str]:
        """Extract text or attribute from elements."""
        return self._call("extract", selector, attr, limit)

    def extract_regex(
        self, pattern: str, from_html: bool = False, limit: int = 100
    ) -> list[str]:
        """Extract matches using regex pattern."""
        return self._call("extract_regex", pattern, from_html, limit)

    def validate_selectors(self, item: str, fields: dict[str, str]) -> dict:
        """Validate CSS selectors on page."""
        return self._call("validate_selectors", item, fields)

    def extract_data(self, item: str, fields_json: str, limit: int = 100) -> dict:
        """Extract structured data from page."""
        return self._call("extract_data", item, fields_json, limit)

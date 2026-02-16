"""HTML parsing utilities with BeautifulSoup integration."""

from __future__ import annotations

from typing import Any, Iterator

from bs4 import BeautifulSoup, Tag


def parse_html(html: str, parser: str = "html.parser") -> BeautifulSoup:
    """Parse HTML string into BeautifulSoup object."""
    return BeautifulSoup(html, parser)


class SoupWrapper:
    """Wrapper around BeautifulSoup with convenience methods."""

    def __init__(self, html: str | None = None, soup: BeautifulSoup | Tag | None = None):
        if soup is not None:
            self._soup: BeautifulSoup | Tag = soup
        elif html is not None:
            self._soup = BeautifulSoup(html, "html.parser")
        else:
            raise ValueError("Either html or soup must be provided")

    @property
    def soup(self) -> BeautifulSoup | Tag:
        """Get underlying BeautifulSoup/Tag object."""
        return self._soup

    def select(self, selector: str) -> list[SoupWrapper]:
        """Select all matching elements."""
        return [SoupWrapper(soup=el) for el in self._soup.select(selector)]

    def select_one(self, selector: str) -> SoupWrapper | None:
        """Select first matching element."""
        el = self._soup.select_one(selector)
        return SoupWrapper(soup=el) if el else None

    def find(self, name: str, **kwargs: Any) -> SoupWrapper | None:
        """Find first element by tag name."""
        el = self._soup.find(name, **kwargs)
        if el and isinstance(el, Tag):
            return SoupWrapper(soup=el)
        return None

    def find_all(self, name: str | None = None, **kwargs: Any) -> list[SoupWrapper]:
        """Find all elements by tag name."""
        elements = self._soup.find_all(name, **kwargs) if name else self._soup.find_all(**kwargs)
        return [SoupWrapper(soup=el) for el in elements if isinstance(el, Tag)]

    def children(self) -> list[SoupWrapper]:
        """Get direct child elements (not recursive)."""
        return [SoupWrapper(soup=el) for el in self._soup.children if isinstance(el, Tag)]

    def text(self, strip: bool = True, separator: str = "") -> str:
        """Get text content."""
        return self._soup.get_text(strip=strip, separator=separator)

    def attr(self, name: str, default: str = "") -> str:
        """Get attribute value."""
        val = self._soup.get(name, default) if hasattr(self._soup, 'get') else default
        return str(val) if val else default

    def attrs(self) -> dict[str, Any]:
        """Get all attributes."""
        return dict(self._soup.attrs) if hasattr(self._soup, 'attrs') else {}

    def html(self) -> str:
        """Get HTML."""
        return str(self._soup)

    # Convenience methods

    def texts(self, selector: str, strip: bool = True) -> list[str]:
        """Get text from all matching elements."""
        return [el.text(strip=strip) for el in self.select(selector)]

    def attrs_list(self, selector: str, attr_name: str) -> list[str]:
        """Get attribute from all matching elements."""
        return [el.attr(attr_name) for el in self.select(selector) if el.attr(attr_name)]

    def links(self, selector: str = "a[href]") -> list[str]:
        """Get all href values."""
        return self.attrs_list(selector, "href")

    def images(self, selector: str = "img[src]") -> list[str]:
        """Get all image src values."""
        return self.attrs_list(selector, "src")

    def __bool__(self) -> bool:
        return self._soup is not None

    def __iter__(self) -> Iterator[SoupWrapper]:
        for child in self.children():
            yield child

    def __repr__(self) -> str:
        return f"<SoupWrapper({getattr(self._soup, 'name', 'soup')})>"


def soup(html: str) -> SoupWrapper:
    """Create SoupWrapper from HTML string."""
    return SoupWrapper(html=html)

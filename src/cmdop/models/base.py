"""
SDKBaseModel - Auto-cleaning Pydantic model for scraped data.

Features:
- Auto-normalize whitespace in str fields
- Extract numbers from text: "$27,471" → 27471, "45 000" → 45000
- Handle Unicode spaces properly
- Convert relative URLs to absolute
- Graceful None handling (uses field defaults)
- Non-strict validation (ignores extra fields, uses defaults)
- from_list() for batch parsing with auto-dedupe

Example:
    from cmdop import SDKBaseModel

    class Item(SDKBaseModel):
        __base_url__ = "https://example.com"

        title: str = ""
        price: int = 0      # "$9,719" → 9719
        url: str = ""       # "/path" → "https://example.com/path"

    # Single item
    item = Item(**raw)

    # Batch with auto-dedupe by URL
    items = Item.from_list(raw_data["items"])
"""

import re
from typing import Any, get_type_hints, get_origin, get_args, Union
from urllib.parse import urljoin

from pydantic import BaseModel, model_validator


class SDKBaseModel(BaseModel):
    """
    Base model with automatic data cleaning for scraped content.

    Features:
    - Normalizes whitespace (including non-breaking spaces)
    - Extracts numbers from text (handles Cyrillic, currency symbols)
    - Converts relative URLs to absolute
    - Uses field defaults when value is None or invalid
    - Ignores extra fields from scraping

    Class attributes:
        __base_url__: Base URL for relative URL conversion
    """

    __base_url__: str = ""

    model_config = {
        "extra": "ignore",           # ignore extra fields
        "validate_default": False,   # don't validate defaults
        "str_strip_whitespace": True,
    }

    @classmethod
    def from_list(
        cls,
        items: list[dict],
        dedupe_by: str = "url",
        filter_by: str = "title",
    ) -> list:
        """
        Parse list of raw dicts with auto-dedupe and filtering.

        Args:
            items: List of raw dicts from extract_data
            dedupe_by: Field to dedupe by (default: "url")
            filter_by: Field that must be non-empty (default: "title")

        Returns:
            Clean, deduped, filtered list of model instances
        """
        parsed = [cls(**item) for item in items]

        # Dedupe by field (usually url)
        if dedupe_by:
            seen = {}
            for item in parsed:
                key = getattr(item, dedupe_by, None)
                if key:
                    seen[key] = item
            parsed = list(seen.values())

        # Filter by non-empty field (usually title)
        if filter_by:
            parsed = [i for i in parsed if getattr(i, filter_by, None)]

        return parsed

    @model_validator(mode="before")
    @classmethod
    def _auto_clean(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        hints = get_type_hints(cls)
        base_url = getattr(cls, "__base_url__", "") or ""
        cleaned = {}

        # Get field defaults
        defaults = {}
        for name, field in cls.model_fields.items():
            if field.default is not None:
                defaults[name] = field.default

        for field_name, field_type in hints.items():
            if field_name.startswith("_"):
                continue

            value = data.get(field_name)

            # Skip None/empty - Pydantic will use default
            if value is None or value == "":
                continue

            # Unwrap Optional[X], Union[X, None] to get actual type
            actual_type = _unwrap_type(field_type)

            # Clean based on type
            if actual_type == int:
                result = _extract_int(value)
                if result is not None:
                    cleaned[field_name] = result
                # else: skip, use default

            elif actual_type == float:
                result = _extract_float(value)
                if result is not None:
                    cleaned[field_name] = result

            elif actual_type == str:
                clean_val = _clean_text(value)
                if clean_val:
                    # Auto-convert URL fields
                    if base_url and _is_url_field(field_name):
                        clean_val = _make_absolute_url(clean_val, base_url)
                    cleaned[field_name] = clean_val

            else:
                # Other types - pass through
                cleaned[field_name] = value

        return cleaned


def _unwrap_type(field_type: Any) -> type:
    """Unwrap Optional[X] or Union[X, None] to get X."""
    origin = get_origin(field_type)

    if origin is Union:
        args = get_args(field_type)
        # Filter out NoneType
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return non_none[0]

    return field_type if isinstance(field_type, type) else str


def _is_url_field(name: str) -> bool:
    """Check if field name indicates a URL."""
    return name == "url" or name.endswith("_url") or name.endswith("_link") or name == "link"


def _clean_text(value: Any) -> str:
    """Normalize whitespace (including non-breaking spaces) and strip."""
    if not isinstance(value, str):
        value = str(value) if value is not None else ""

    # Replace non-breaking spaces and other unicode spaces with regular space
    value = re.sub(r'[\xa0\u2000-\u200b\u202f\u205f\u3000]', ' ', value)

    # Normalize whitespace
    return " ".join(value.split())


def _extract_int(value: Any) -> int | None:
    """
    Extract integer from text.

    Handles:
    - Currency: "$27,471" → 27471, "€1.500" → 1500
    - Spaces: "9 719 000" → 9719000
    - Units: "45 000 km" → 45000
    - Non-breaking spaces: "9\xa0719" → 9719
    """
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if not isinstance(value, str):
        return None

    # Normalize spaces first
    value = re.sub(r'[\xa0\u2000-\u200b\u202f\u205f\u3000\s]', '', value)

    # Remove currency symbols and units
    value = re.sub(r'[₽$€¥£руб\.kmкм]', '', value, flags=re.IGNORECASE)

    # Remove thousand separators (commas, spaces already removed)
    value = value.replace(',', '')

    # Extract digits (with optional decimal point)
    match = re.search(r'[\d.]+', value)
    if not match:
        return None

    try:
        return int(float(match.group()))
    except ValueError:
        return None


def _extract_float(value: Any) -> float | None:
    """Extract float from text, similar to _extract_int but keeps decimals."""
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None

    # Normalize spaces
    value = re.sub(r'[\xa0\u2000-\u200b\u202f\u205f\u3000\s]', '', value)

    # Remove currency/units
    value = re.sub(r'[₽$€¥£руб\.kmкм]', '', value, flags=re.IGNORECASE)
    value = value.replace(',', '')

    match = re.search(r'[\d.]+', value)
    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def _make_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute."""
    if not url or not base_url:
        return url

    # Already absolute
    if url.startswith(("http://", "https://", "//")):
        return url

    return urljoin(base_url, url)

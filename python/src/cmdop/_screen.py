"""A screenshot as bytes: the machine answers base64 PNG inside the JSON; this decodes it (the twin of `screen.ts`)."""

from __future__ import annotations

import base64
from dataclasses import dataclass

from .generated import models as m

_MIME = {"png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpeg", "webp": "image/webp"}


@dataclass(frozen=True)
class DecodedImage:
    """A decoded picture: `data` is the encoded file (PNG), ready to write to a `.png`."""

    data: bytes
    mime: str
    width: int
    height: int


@dataclass(frozen=True)
class Screenshot:
    """What `box.screenshot()` returns. Pixel coordinates of every pointer tool are pixels of `image` (see `geometry`)."""

    image: DecodedImage
    geometry: m.Geometry
    audit_id: str
    """Id of the audit line and the saved copy on the machine."""


def decode_image(image: m.Image) -> DecodedImage:
    """Decodes the base64 `data` of a machine picture. Raises on a format this SDK does not know, rather than guess."""
    mime = _MIME.get(image.format.lower())
    if mime is None:
        raise ValueError(f"unknown image format {image.format!r}")
    return DecodedImage(base64.b64decode(image.data), mime, image.width, image.height)


def to_screenshot(out: m.ScreenCaptureOut) -> Screenshot:
    return Screenshot(decode_image(out.image), out.geometry, out.audit_id)

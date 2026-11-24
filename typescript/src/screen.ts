/** A screenshot as bytes (@dev/completed/computer-use/10_computer_use.md, D7): the machine answers base64 PNG inside the JSON; this decodes it. */

import type { Geometry, Image, ScreenCaptureOut } from "./generated/tools.gen.ts";

/** A decoded picture: `bytes` are the encoded file (PNG), ready for `new Blob([bytes], { type: mime })` or a file. */
export interface DecodedImage {
  bytes: Uint8Array;
  mime: string;
  width: number;
  height: number;
}

/** What `client.screenshot` returns. Pixel coordinates of every pointer tool are pixels of `image` (see `geometry`). */
export interface Screenshot {
  image: DecodedImage;
  geometry: Geometry;
  /** Id of the audit line and the saved copy on the machine. */
  auditId: string;
}

const MIME: Record<string, string> = { png: "image/png", jpeg: "image/jpeg", jpg: "image/jpeg", webp: "image/webp" };

/** Decodes the base64 `data` of a machine picture. Throws on a format this SDK does not know, rather than guess a mime. */
export function decodeImage(image: Image): DecodedImage {
  const mime = MIME[image.format.toLowerCase()];
  if (!mime) throw new Error(`unknown image format ${JSON.stringify(image.format)}`);
  const raw = atob(image.data);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i += 1) bytes[i] = raw.charCodeAt(i);
  return { bytes, mime, width: image.width, height: image.height };
}

export function toScreenshot(out: ScreenCaptureOut): Screenshot {
  return { image: decodeImage(out.image), geometry: out.geometry, auditId: out.audit_id };
}

/**
 * The small streaming boundary used by `/api/v1/call/stream`.
 *
 * The endpoint deliberately stays outside ordinary JSON code generation: its
 * response is a sequence of JSON values, not one JSON document. Keeping the
 * framing here gives the SDK one place to handle split UTF-8 chunks, blank
 * lines and a final line without a trailing newline.
 */

export type NdjsonLine<TChunk, TAnswer> =
  | { chunk: TChunk; seq: number }
  | { sealed_chunk: string; seq: number }
  | TAnswer;

export async function readNdjson<T>(
  body: ReadableStream<Uint8Array>,
  onLine: (line: T) => void | Promise<void>,
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let rest = "";

  const emit = async (line: string) => {
    const text = line.trim();
    if (text) await onLine(JSON.parse(text) as T);
  };

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    rest += decoder.decode(value, { stream: true });
    let newline: number;
    while ((newline = rest.indexOf("\n")) >= 0) {
      await emit(rest.slice(0, newline));
      rest = rest.slice(newline + 1);
    }
  }
  rest += decoder.decode();
  await emit(rest);
}

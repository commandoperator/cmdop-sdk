# Files and screenshots

File tools act on the selected computer. Screenshot helpers decode the returned image for your program.

**In short:** Use `box.fs.read` with `read` access and `box.screenshot()` with `screen` access plus OS permission.

## Read a file

Replace the example path with an existing non-sensitive file on the selected machine.
Requires the `read` risk class.

```ts
const file = await box.fs.read({ path: "/tmp/notes.txt" });
console.log(file.encoding, file.truncated, file.data);
```

```python
file = box.fs.read(path="/tmp/notes.txt")
print(file.encoding, file.truncated, file.data)
```

`encoding` distinguishes UTF-8 text from base64 bytes. If `truncated` is true, read further using
`offset`; do not treat a partial read as the complete file. The [fs_read](https://docs.cmdop.ai/reference/tools/fs_read)
reference owns limits and argument details. Reads of credential paths can be refused.

## Change a file

`box.fs.write` and `box.fs.edit` require `write` access. Read the tool reference before writing:
a write can replace existing data. Use the documented precondition fields when available.
Deletion is a separate tool with its own risk class.

## Capture a screen

Requires `screen` access and the machine's OS screen-capture permission.
TypeScript `await box.screenshot()` returns decoded `image.bytes` and `image.mime`;
Python `box.screenshot()` returns `image.data` and `image.mime`. Both include geometry.
See [screen_capture](https://docs.cmdop.ai/reference/tools/screen_capture) for the requested capture region.

Screenshots may contain private information. On
[permission_missing](https://docs.cmdop.ai/reference/errors/permission_missing), follow the supplied human action on
the machine before retrying. Enabling a risk class cannot grant an OS permission.

[SDK](README.md) · [Errors and cancellation](errors-and-cancellation.md)

# Files

Read, write, list files on remote machines. No scp/sftp needed.

```python
# Set target machine once
await client.files.set_machine("my-server")

# File operations
files = await client.files.list("/var/log", include_hidden=True)
content = await client.files.read("/etc/nginx/nginx.conf")
await client.files.write("/tmp/config.json", b'{"key": "value"}')

# More operations
await client.files.copy("/src", "/dst")
await client.files.move("/old", "/new")
await client.files.mkdir("/new/dir")
await client.files.delete("/tmp/old", recursive=True)
info = await client.files.info("/path/file.txt")
```

# Download

Download files from URLs via remote server.

```python
from pathlib import Path

async with AsyncCMDOPClient.remote(api_key="cmdop_xxx") as client:
    # Set target machine
    await client.download.set_machine("my-server")
    client.download.configure(api_key="cmdop_xxx")

    result = await client.download.url(
        url="https://example.com/large-file.zip",
        local_path=Path("./large-file.zip"),
    )

    if result.success:
        print(result)  # DownloadResult(ok, 139.2MB, 245.3s, 0.6MB/s)
```

Handles cloud relay limits automatically:
- Small files (≤10MB): Direct chunked transfer
- Large files (>10MB): Split on remote, download parts

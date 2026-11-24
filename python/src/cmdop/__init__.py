"""cmdop: your machines' tools from a program, the same tools agents use through MCP.

```python
import cmdop
with cmdop.connect() as c:            # CMDOP_TOKEN, CMDOP_URL
    box = c.machine("box")
    print(box.run("uptime").stdout)
```
"""

from ._async import AsyncClient, AsyncMachine, AsyncRun, connect_async
from ._client import Client, Machine, Piece, Run, connect
from ._errors import CarrierError, CmdopError
from .carriers import AsyncMemoryCarrier, MemoryCarrier
from .generated.call import ENVELOPE_MAX_BYTES, ERROR_CODES, PIECE_MAX_BYTES
from .generated.tools import TOOLS

__all__ = [
    "ENVELOPE_MAX_BYTES",
    "ERROR_CODES",
    "PIECE_MAX_BYTES",
    "TOOLS",
    "AsyncClient",
    "AsyncMachine",
    "AsyncMemoryCarrier",
    "AsyncRun",
    "CarrierError",
    "Client",
    "CmdopError",
    "Machine",
    "MemoryCarrier",
    "Piece",
    "Run",
    "connect",
    "connect_async",
]

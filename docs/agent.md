# AI Agent

Run AI tasks with structured, typed output.

```python
from pydantic import BaseModel, Field

class ServerHealth(BaseModel):
    hostname: str
    cpu_percent: float = Field(description="CPU usage percentage")
    memory_percent: float
    disk_free_gb: float
    issues: list[str] = Field(description="List of detected issues")

await client.agent.set_machine("my-server")
result = await client.agent.run(
    prompt="Check server health and report any issues",
    output_model=ServerHealth,
)

# Typed response - not just text!
health: ServerHealth = result.data
if health.cpu_percent > 90:
    alert(f"{health.hostname} CPU critical!")
```

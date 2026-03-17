# Skills

Run predefined AI workflows on remote machines. Skills are reusable prompt templates with tool access.

## Basic Usage

```python
await client.skills.set_machine("my-server")

# List available skills
skills = await client.skills.list()
for skill in skills:
    print(f"{skill.name}: {skill.description} ({skill.origin})")

# Inspect a skill
detail = await client.skills.show("code-review")
if detail.found:
    print(detail.content)   # System prompt markdown
    print(detail.source)    # File path on machine

# Run a skill
result = await client.skills.run("code-review", "Review the auth module")
print(result.text)
print(f"Took {result.duration_seconds}s, {result.usage.total_tokens} tokens")
```

## Structured Output

```python
from pydantic import BaseModel

class Review(BaseModel):
    score: int
    summary: str
    issues: list[str]

result = await client.skills.run(
    "code-review",
    "Review the auth module",
    output_model=Review,
)
review: Review = result.data
print(f"Score: {review.score}/10")
```

## Custom Options

```python
from cmdop import SkillRunOptions

result = await client.skills.run(
    "summarize",
    "Summarize the project README",
    options=SkillRunOptions(model="openai/gpt-4o", timeout_seconds=120),
)
```

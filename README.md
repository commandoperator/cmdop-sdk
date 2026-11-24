# CMDOP SDK

Your machines' tools from a program, in TypeScript and Python: the same tools AI agents use through MCP, with the
same rules and the same record of every call.

| Language | Install | Source |
|---|---|---|
| TypeScript / Node | `npm install @cmdop/sdk` | [`typescript/`](typescript/) |
| Python | `pip install cmdop` | [`python/`](python/) |

```ts
import { connect } from "@cmdop/sdk";

const box = connect().machine("box");        // CMDOP_TOKEN, CMDOP_URL
console.log((await box.run("uptime")).stdout);
```

```python
import cmdop

with cmdop.connect() as c:                   # CMDOP_TOKEN, CMDOP_URL
    print(c.machine("box").run("uptime").stdout)
```

Both packages are generated from one tool contract, so a tool, its arguments and its result are the same in each.
[`vectors/carrier.json`](vectors/carrier.json) holds the cases every client must pass.

This repository is the published source of each release (`v<version>` tags); issues are welcome here.

Docs: https://docs.cmdop.ai · License: [MIT](LICENSE)

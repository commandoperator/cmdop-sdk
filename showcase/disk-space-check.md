# Is there room for the next build?

Before sending a build to a home server, ask how much space is available on the
volume that holds its build directory. Choose the computer and mount explicitly.
For example, if the build writes to the root filesystem:

> Use CMDOP to check the root filesystem on my selected computer. Show the free
> space in GiB and the percentage available. Flag it if less than 10% is free.
> If the computer is offline or the mount is missing, report that the check
> could not be completed. Leave the files as they are.

In a manual check on November 26, 2026, the caller selected an online Mac by ID
and called `sys_info` through CMDOP MCP. Its root filesystem had less than 1%
available, which triggered the 10% threshold. The check used read access. It
made no changes to the machine.

## Use the result in an application

Choose the machine ID from `machines_list`. The Python and TypeScript SDKs
return the mount, available bytes and total bytes for each filesystem in
`sys.info`. Match the requested mount exactly. For a build on a separate data
volume, use that mount instead of `/`.

- Show free GiB as available bytes divided by 1,073,741,824.
- For a positive total, flag the volume when available bytes multiplied by 100
  are less than total bytes multiplied by the percentage threshold.
- If the mount is absent, the total is zero or the call fails, report the
  measurement as unavailable. A missing measurement cannot clear an alert.

## Run the SDK example

Open the [Python program](https://github.com/commandoperator/cmdop-sdk/blob/a9f856edeba61e18d09c1f20e500b44b7ad054b0/examples/python/disk-space.py) or
the [TypeScript program](https://github.com/commandoperator/cmdop-sdk/blob/a9f856edeba61e18d09c1f20e500b44b7ad054b0/examples/typescript/disk-space.ts).
Both run one read-only check. In an SDK checkout at that revision, follow the
[connection setup](../docs/examples/run.md) and set `CMDOP_MACHINE` to the
selected machine ID. To see the measurement from Python, run:

```sh
CMDOP_MOUNT=/ uv run --with cmdop==3.6.0 python examples/python/disk-space.py
```

The JSON result includes the mount, free GiB and `below_10_percent`. Set
`CMDOP_MOUNT` to the mounted volume holding your builds. To check that both
language entry points run, use `ONLY=disk-space bash examples/run.sh` from
the same checkout. The runner reports pass or failure for each language.

[System information tool reference](https://docs.cmdop.ai/reference/tools/sys_info)

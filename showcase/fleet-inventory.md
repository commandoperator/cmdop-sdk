# Which of my computers is online?

You have a Linux box and a Mac. Before choosing where to run a job, ask your
connected chat for the inventory and inspect the computer you intend to use.

> Using CMDOP, list my computers and show which ones are online. For my Mac
> only, report its CPU architecture, CPU count and available memory. If there
> are several Macs, ask me which one to inspect.

In a November 26, 2026 run, CMDOP listed two online computers, one Linux and
one macOS. The caller selected the Mac by its returned machine ID. Its
`sys_info` response reported `aarch64`, eight CPUs and available memory.
The Linux machine was listed only. The two calls used read access throughout.

## Use it in your own application

Call `machines_list` to populate the inventory. Keep the returned ID alongside
each display name. When the user selects a computer, check its state and
whether it offers `sys_info` before requesting details. Availability and
free memory describe the instant of the call.

To inspect a whole fleet, try the [Python fleet example](https://github.com/commandoperator/cmdop-sdk/blob/a9f856edeba61e18d09c1f20e500b44b7ad054b0/examples/python/fleet.py)
or its [TypeScript counterpart](https://github.com/commandoperator/cmdop-sdk/blob/a9f856edeba61e18d09c1f20e500b44b7ad054b0/examples/typescript/fleet.ts).
Both select by ID and report availability per machine. From an SDK checkout at
that revision, run `ONLY=fleet bash examples/run.sh` with read access configured.

[Configure the SDK](../docs/quickstart.md) · [More things to build](README.md)

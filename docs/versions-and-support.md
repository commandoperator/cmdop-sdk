# Versions and support

Both languages share a version; the machine program has a separate version and tool availability.

**In short:** Check your installed package version, the selected machine's advertised tools and the public release notes before reporting an issue.

## Package versions

```bash
npm list @cmdop/sdk
python -m pip show cmdop
```

Get releases from [npm](https://www.npmjs.com/package/@cmdop/sdk),
[PyPI](https://pypi.org/project/cmdop/) and the
[SDK repository](https://github.com/commandoperator/cmdop-sdk).
The 3.x SDK uses `connect()`; examples for the older 2.x client API do not apply.

## Runtimes and machines

The TypeScript package targets Node.js 20+. Python requires 3.10+.
A program's runtime is separate from the remote computer's operating system.
The machine program is available on macOS and Linux; see
[feature status](https://docs.cmdop.ai/help/feature-status) for platform and client availability.

An older machine may not provide a tool added by a newer SDK.
Check its advertised tools and handle `unknown_tool`. Within a major SDK release,
public contract changes are additive; see the [changelog](https://docs.cmdop.ai/help/changelog).

## Public source

The SDK is MIT-licensed. Its public repository contains the language packages and documentation;
this does not make the whole CMDOP platform open source.
Calls encrypted end to end from paired clients are not included in the published SDK packages;
see [sealed calls](https://docs.cmdop.ai/concepts/sealed-calls).

## Report a problem

Open an [SDK issue](https://github.com/commandoperator/cmdop-sdk/issues) with package version,
runtime/OS, tool name, error code, expected outcome and a minimal reproducer.
Remove tokens, private addresses, machine ids and personal file contents before sharing.

[SDK](README.md) · [Errors](errors-and-cancellation.md)

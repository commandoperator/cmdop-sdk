"""The AI agent programs on each online machine (Claude Code, Codex), and with AGENT_PROMPT=1 one question to the
default one. Listing needs a `read` grant; asking needs the `agent` class on the token and in the machine's ceiling."""

import os

import cmdop

with cmdop.connect() as c:  # CMDOP_TOKEN, CMDOP_URL
    for m in [m for m in c.machines() if m["online"]]:
        box = c.machine(m["name"])
        try:
            listing = box.agent.list()
        except cmdop.CmdopError as e:
            print(f"  {m['name']}: no agent tools ({e.code})")
            continue
        names = ", ".join(f"{a.id} ({a.tier}{', busy' if a.busy else ''})" for a in listing.agents)
        print(f"  {m['name']}: {names or 'no agent allowed'}; default {listing.default or 'none'}")
        if os.environ.get("AGENT_PROMPT") == "1" and listing.default:
            answer = box.agent.prompt(prompt="In one sentence: what is this machine?")
            print(f"    {answer.agent} {answer.state}: {answer.text or ''}")

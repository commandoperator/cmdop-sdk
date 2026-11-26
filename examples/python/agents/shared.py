"""Bounded, explicit-agent prompt example. No calls occur without the opt-in and target."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Mapping

import cmdop


@dataclass(frozen=True)
class Profile:
    agent: str
    prompt: str = "Reply with exactly CMDOP_AGENT_OK and no other text. Do not use tools."
    expected: str = "CMDOP_AGENT_OK"


class ExampleError(Exception):
    """A bounded diagnostic label; never include remote messages or credentials."""


def settings(env: Mapping[str, str]) -> str:
    if env.get("AGENT_PROMPT") != "1":
        raise ExampleError("opt_in_required: set AGENT_PROMPT=1")
    if not all(env.get(key, "").strip() for key in ("CMDOP_URL", "CMDOP_TOKEN", "CMDOP_MACHINE")):
        raise ExampleError("setup_required: CMDOP_URL, CMDOP_TOKEN, CMDOP_MACHINE")
    return env["CMDOP_MACHINE"].strip()


def prompt(client: cmdop.Client, machine_id: str, profile: Profile) -> dict[str, object]:
    rows = [row for row in client.machines_list(deadline=15) if row.id == machine_id]
    if len(rows) != 1 or rows[0].state != "online":
        raise ExampleError("target_unavailable")
    if not {"agent_list", "agent_prompt"}.issubset(rows[0].tools):
        raise ExampleError("agent_tools_unavailable")
    box = client.machine(machine_id)
    agents = [row for row in box.agent.list(deadline=15).agents if row.id == profile.agent]
    if len(agents) != 1 or not agents[0].installed:
        raise ExampleError("requested_agent_unavailable")
    if agents[0].busy:
        raise ExampleError("requested_agent_busy")
    if agents[0].tier not in ("text_only", "read_only"):
        raise ExampleError("unsupported_tier")
    answer = box.agent.prompt(
        agent=profile.agent, tier="text_only", prompt=profile.prompt, wait_secs=30, deadline=45
    )
    if answer.agent != profile.agent or answer.tier != "text_only":
        raise ExampleError("unexpected_agent_or_tier")
    # Preserve the handle when still running; never report a final answer or retry the prompt.
    if answer.state == "running":
        return {"agent": profile.agent, "state": "running", "task": answer.task, "session": answer.session}
    if answer.state != "done":
        raise ExampleError("agent_did_not_finish")
    if (answer.text or "").strip() != profile.expected:
        raise ExampleError("unexpected_answer")
    return {"agent": profile.agent, "state": "done", "answer": profile.expected}


def main(profile: Profile) -> None:
    try:
        machine_id = settings(os.environ)
        with cmdop.connect() as client:
            result = prompt(client, machine_id, profile)
        print(json.dumps(result))
        if result["state"] == "running":
            raise SystemExit(3)
    except Exception as error:
        label = str(error) if isinstance(error, ExampleError) else (
            type(error).__name__ if isinstance(error, (cmdop.CmdopError, cmdop.CarrierError)) else "unexpected_error"
        )
        print(json.dumps({"state": "failed", "reason": label}), file=sys.stderr)
        raise SystemExit(1) from None

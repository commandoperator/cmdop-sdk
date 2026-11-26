"""List installed agents only. Prompts have separate named, explicitly opted-in examples."""

import cmdop

with cmdop.connect() as client:
    for row in client.machines_list():
        if row.state != "online" or "agent_list" not in row.tools:
            continue
        listing = client.machine(row.id).agent.list()
        print(row.name, [(agent.id, agent.tier, agent.busy) for agent in listing.agents])

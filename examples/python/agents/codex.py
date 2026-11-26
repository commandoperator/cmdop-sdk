"""Ask Codex explicitly; requires AGENT_PROMPT=1 and a nominated machine ID."""

from shared import Profile, main

CODEX = Profile(agent="codex")

if __name__ == "__main__":
    main(CODEX)

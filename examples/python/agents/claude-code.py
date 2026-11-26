"""Ask Claude Code explicitly; its installation/authentication must work on this machine."""

from shared import Profile, main

CLAUDE_CODE = Profile(agent="claude-code")

if __name__ == "__main__":
    main(CLAUDE_CODE)

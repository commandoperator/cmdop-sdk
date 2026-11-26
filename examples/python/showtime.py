"""The server's own tools, no machine needed: the demo guide an agent follows, and what is running now."""

import cmdop

with cmdop.connect() as c:  # CMDOP_TOKEN, CMDOP_URL
    guide = c.showtime_guide(language="English")
    if len(guide) < 200:
        raise SystemExit("showtime_guide gave no guide")
    print(f"showtime_guide: {len(guide)} characters; first line: {guide.splitlines()[0]}")
    now = c.tasks_list()
    print(f"tasks_list: {len(now.tasks)} started through cmdop, {len(now.outside)} machines with other processes")

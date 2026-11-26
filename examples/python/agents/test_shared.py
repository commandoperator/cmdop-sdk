"""Offline behavior checks using the real SDK and its memory carrier, never an installed agent."""

import unittest

import cmdop

from shared import ExampleError, Profile, prompt, settings


class PromptTests(unittest.TestCase):
    def run_case(self, agent="codex", *, presence="online", listed="codex", busy=False,
                 state="done", text="CMDOP_AGENT_OK", answered=None):
        seen = []
        row = dict(id="fixture", name="fixture", online=True, os="linux", arch="x86_64", own_name="fixture",
                   dirty=False, epoch=1, last_seen=0, program="0.1.16", since=0, state=presence,
                   tools=["agent_list", "agent_prompt"])

        def serve(req):
            seen.append(req)
            if req["tool"] == "machines_list":
                yield {"ok": [row]}
            elif req["tool"] == "agent_list":
                yield {"ok": {"agents": [dict(id=listed, name=listed, protocol="headless_json",
                    installed=True, tier="text_only", resume=True, busy=busy)], "default": listed}}
            elif req["tool"] == "agent_prompt":
                yield {"ok": dict(agent=answered or agent, state=state, task=7,
                                   tier="text_only", text=text, session="fixture-session")}
            else:
                raise AssertionError("unexpected dispatch")

        with cmdop.connect(carrier=cmdop.MemoryCarrier(serve)) as client:
            try:
                return prompt(client, "fixture", Profile(agent)), seen
            finally:
                self.seen = seen

    def test_opt_in_precedes_setup(self):
        with self.assertRaisesRegex(ExampleError, "opt_in_required"):
            settings({})
        with self.assertRaisesRegex(ExampleError, "setup_required"):
            settings({"AGENT_PROMPT": "1"})

    def test_exact_agent_is_sent_for_each_named_profile(self):
        for agent in ("codex", "claude-code"):
            result, seen = self.run_case(agent, listed=agent)
            self.assertEqual(result["state"], "done")
            request = seen[-1]
            self.assertEqual(request["args"]["agent"], agent)
            self.assertEqual(request["args"]["tier"], "text_only")
            self.assertEqual(request["machine"], "fixture")
            self.assertEqual(request["deadline_ms"], 45000)

    def test_wrong_agent_never_falls_back_to_default(self):
        with self.assertRaisesRegex(ExampleError, "requested_agent_unavailable"):
            self.run_case(listed="claude-code")
        self.assertEqual([r["tool"] for r in self.seen], ["machines_list", "agent_list"])

    def test_paused_online_target_stops_before_agent_calls(self):
        with self.assertRaisesRegex(ExampleError, "target_unavailable"):
            self.run_case(presence="paused")
        self.assertEqual(len(self.seen), 1)

    def test_busy_agent_does_not_receive_another_prompt(self):
        with self.assertRaisesRegex(ExampleError, "requested_agent_busy"):
            self.run_case(busy=True)
        self.assertEqual(len(self.seen), 2)

    def test_wrong_answer_and_failed_run_are_not_success(self):
        for state, text in (("done", "other"), ("failed", "CMDOP_AGENT_OK"), ("stopped", "")):
            with self.assertRaises(ExampleError):
                self.run_case(state=state, text=text)

    def test_answer_from_another_agent_is_rejected(self):
        with self.assertRaisesRegex(ExampleError, "unexpected_agent_or_tier"):
            self.run_case(answered="claude-code")

    def test_running_keeps_handle_without_claiming_a_final_answer(self):
        result, seen = self.run_case(state="running", text="")
        self.assertEqual(result, dict(agent="codex", state="running", task=7, session="fixture-session"))
        self.assertEqual(len(seen), 3)


if __name__ == "__main__":
    unittest.main()

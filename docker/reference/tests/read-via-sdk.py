"""Run the image's external SDK reader against a loopback contour fixture."""
import json
import os
from pathlib import Path
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

path = "/opt/report/build.json"
report_text = Path(path).read_text()
report = json.loads(report_text)
requests = []


class Contour(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        call = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        requests.append((self.path, self.headers.get("Authorization"), call))
        response = json.dumps(self.server.answer).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def run(server, data, *, truncated=False):
    server.answer = {"ok": {"path": path, "encoding": "utf8", "offset": 0,
                            "size": len(data.encode()), "truncated": truncated, "data": data}}
    env = dict(os.environ, CMDOP_URL=f"http://127.0.0.1:{server.server_port}",
               CMDOP_TOKEN="fixture", CMDOP_MACHINE="report-machine")
    result = subprocess.run(["python", "/opt/report/read_via_sdk.py"], env=env,
                            capture_output=True, text=True, timeout=20)
    assert len(requests) == 1, requests
    endpoint, authorization, call = requests.pop()
    assert (endpoint, authorization) == ("/api/v1/call", "Bearer fixture")
    assert (call["machine"], call["tool"], call["args"], call["deadline_ms"]) == (
        "report-machine", "fs_read", {"path": path}, 15000)
    return result


with HTTPServer(("127.0.0.1", 0), Contour) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        ok = run(server, report_text)
        assert ok.returncode == 0 and json.loads(ok.stdout) == report, ok.stderr
        for data, truncated, message in [
            (report_text, True, "complete UTF-8"),
            (json.dumps(dict(report, tests_failed=False)), False, "Unexpected build report"),
            ("{}", False, "Unexpected build report"),
            ("{", False, "invalid report JSON"),
        ]:
            failed = run(server, data, truncated=truncated)
            assert failed.returncode != 0 and not failed.stdout and message in failed.stderr, failed
    finally:
        server.shutdown()

"""Run small Moss API checks with synthetic inputs and a bounded task."""
import json
import os
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "https://inference.moss.dev/v1"
AUTH = f'{os.environ["MOSS_PROJECT_ID"]}:{os.environ["MOSS_PROJECT_KEY"]}'
SCHEMA = {
    "type": "object",
    "properties": {"heading": {"type": "string"}},
    "required": ["heading"],
}


def request(path, payload=None):
    req = Request(
        BASE + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {AUTH}", "Content-Type": "application/json"},
    )
    started = time.monotonic()
    try:
        with urlopen(req, timeout=25) as response:
            return response.status, json.load(response), round((time.monotonic() - started) * 1000)
    except HTTPError as error:
        try:
            body = json.load(error)
        except ValueError:
            body = {}
        return error.code, body, round((time.monotonic() - started) * 1000)


def report(label, **values):
    print(json.dumps(dict(case=label, **values)), flush=True)


def main():
    status, body, ms = request("/responses", {
        "model": "moss/fastlane-1",
        "input": "Return only this exact text, with no formatting: MOSS-SMOKE-OK",
    })
    output = "".join(
        item.get("text", "")
        for message in body.get("output", [])
        for item in message.get("content", [])
        if item.get("type") == "output_text"
    )
    report("inference exact text", http=status, elapsed_ms=ms, text=output,
           exact=output.strip() == "MOSS-SMOKE-OK")

    task = {
        "goal": "Read the public example page and return its main heading. Read only.",
        "environment": {"type": "browser", "start_url": "https://example.com/"},
        "model": "moss-balanced",
        "output_schema": SCHEMA,
        "limits": {"max_runtime_seconds": 120, "max_cost_usd": 0.10},
    }
    invalid = dict(task, limits={"max_runtime_seconds": 1, "max_cost_usd": 0.01})
    status, body, _ = request("/tasks", invalid)
    error = body.get("error", {})
    report("tasks runtime below documented minimum", http=status,
           error={field: error.get(field) for field in ("code", "message", "param")}
           if isinstance(error, dict) else error)
    status, body, _ = request("/tasks", task)
    report("tasks create", http=status, status=body.get("status"))
    if status >= 300 or not body.get("id"):
        return
    task_id = body["id"]
    deadline = time.monotonic() + 145
    while time.monotonic() < deadline:
        time.sleep(4)
        status, body, _ = request(f"/tasks/{task_id}")
        state = body.get("status")
        if status >= 300 or state in {"completed", "failed", "cancelled"}:
            report("tasks terminal", http=status, status=state,
                   result=body.get("result"), verification=body.get("verification"), usage=body.get("usage"), error=body.get("error"))
            return
    report("tasks poll deadline")


if __name__ == "__main__":
    main()

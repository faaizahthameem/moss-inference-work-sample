# Moss Inference work sample

Run the API checks with Python 3 using `python smoke.py`. The script reads MOSS_PROJECT_ID and MOSS_PROJECT_KEY from the environment. Keep both out of version control. The API script was written and run with ChatGPT assistance.

# Moss portal test log

Run on November 24, 2026. These results came from the signed-in portal.

## Onboarding
Chose Just exploring, skipped the referral question, and kept sample data.
The sample screen said it created product-search-context with 100 sample
documents, but its search and suggested prompts stayed disabled on two
checks. The Inference Playground later displayed No indexes.

## Inference Playground
Model: Fastlane 1. No index selected.
Input: Return only this exact text, with no formatting: MOSS-SMOKE-OK
Output: MOSS-SMOKE-OK
Portal metrics: 191 ms first token, 191 ms total, 104 input tokens,
8 output tokens, 0 ms retrieval. One run.

## Tasks
Goal: Read the public example page and return its main heading. Read only,
without submitting anything.
Start URL: https://example.com/
Model: Moss Balanced. Limits: 2 minutes and $0.10.
Schema: {"type":"object","properties":{"heading":{"type":"string"}},"required":["heading"]}
Result: {"heading":"Example Domain"}
Portal metrics: Succeeded, schema matched, 23 seconds, five steps, $0.088.

## Python documentation navigation
Start URL: https://docs.python.org/3/
Goal: Follow Library Reference, find the JSON module, and return its URL and the string and file decoding functions.
Model: Moss Balanced. Limits: 2 minutes and $0.25.
Result: {"url":"https://docs.python.org/3/library/json.html","from_file":"json.load(fp)","from_string":"json.loads(s)"}
Portal metrics: Succeeded, schema matched, 26 seconds, six steps, $0.062.
Verified both functions against the official JSON module documentation.

## Budget limit check
A separate heading lookup with a $0.01 limit stopped with budget_exceeded
and no answer. The portal displayed $0.024 in spend.

## Direct API results

```jsonl
{"case": "inference exact text", "http": 200, "elapsed_ms": 6481, "text": "MOSS-SMOKE-OK", "exact": true}
{"case": "tasks runtime below documented minimum", "http": 400, "error": {"code": "invalid_request_error", "message": "limits.max_runtime_seconds must be a number from 60 to 7200", "param": null}}
{"case": "tasks create", "http": 202, "status": "queued"}
{"case": "tasks terminal", "http": 200, "status": "completed", "result": {"output": {"heading": "Example Domain"}, "output_text": "{\"heading\":\"Example Domain\"}"}, "verification": {"method": "output_schema", "passed": true}, "usage": {"cost": {"model_usd": 0.057221, "total_usd": 0.057554, "browser_usd": 0.0003333333333333333, "traffic_usd": null}, "steps": 4, "cost_usd": 0.057221, "model_calls": 5, "input_tokens": 58687, "output_tokens": 428, "browser_minutes": 0.37, "browser_seconds": 22, "browser_traffic_mb": null, "cached_input_tokens": 42458}, "error": null}
```

The first Tasks request returned HTTP 400 because start_url was at the top level. Moving it into environment fixed that request. The Python documentation lookup was a separate portal run.

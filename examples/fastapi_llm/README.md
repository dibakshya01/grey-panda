# Guard a FastAPI LLM endpoint

This runnable example follows the public SDK pipeline: `PromptGuardrail` →
`DLPScanner` → `call_your_llm` → `OutputGuardrail`. It demonstrates input
validation (LLM01), sensitive-data redaction (LLM02), and output handling
(LLM10). The default model is an offline echo stub: no API key or model download.

From the repository root, with Python 3.10+:

```bash
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -e . -r examples/fastapi_llm/requirements.txt
python -m uvicorn examples.fastapi_llm.app:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/docs> to try `POST /chat`:

```json
{"prompt": "Please explain retrieval augmented generation."}
```

Known injection such as `ignore previous instructions` returns HTTP 400 before
the model is called. Structured PII is redacted before the call. HTML in the
model response is escaped; the endpoint returns JSON, not executable HTML.
Empty input or input over 50,000 characters returns HTTP 422.

Replace `call_your_llm` with your synchronous model call to use a real provider.
The route is synchronous so FastAPI runs blocking calls in its worker pool.
The source comments show the unguarded call and the guarded pipeline.

These pattern-based controls are one layer of defense, not a guarantee against
all injection or sensitive-data leakage. Authentication, rate limits, provider
timeouts, and application-specific policies remain deployment concerns.

Run the offline HTTP tests after installing the example requirements:

```bash
python -m unittest discover -s tests -p test_fastapi_llm.py -v
```

FastAPI and HTTPX are example-only dependencies; the Grey Panda package keeps
its zero-runtime-dependency contract.

"""Offline FastAPI example using the public Grey Panda SDK."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from greypanda import DLPScanner, OutputGuardrail, PromptGuardrail

app = FastAPI(title="Grey Panda guarded LLM")
guard = PromptGuardrail()
dlp = DLPScanner()
out = OutputGuardrail()


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=50_000)


class ChatResponse(BaseModel):
    answer: str


def call_your_llm(prompt: str) -> str:
    """Deterministic local stub; replace this function with your model client."""
    return f"You asked: {prompt}"


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    # 改造前：直接把用户输入传给模型，再返回未经处理的输出。
    # 改造后：先阻断已知注入，再脱敏，最后处理模型输出中的 HTML。
    try:
        safe = guard.assert_safe(request.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Prompt rejected by input guardrail") from exc
    clean = dlp.redact(safe)
    reply = call_your_llm(clean)
    answer = out.sanitize(reply).sanitized_text
    return ChatResponse(answer=answer or "")

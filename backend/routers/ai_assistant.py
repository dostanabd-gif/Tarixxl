from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from ai_engine.ollama_service import OllamaServiceError, ask_ollama
from core.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=3, max_length=5000)
    system: str | None = Field(default=None, max_length=1000)


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse, summary="AI-помощник (Ollama)")
def chat(payload: ChatRequest, _: CurrentUser = Depends(get_current_user)):
    try:
        answer = ask_ollama(prompt=payload.prompt, system=payload.system)
    except OllamaServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"answer": answer}

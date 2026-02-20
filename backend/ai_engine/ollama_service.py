import httpx

from core.config import settings


class OllamaServiceError(RuntimeError):
    pass


def ask_ollama(prompt: str, system: str | None = None) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", "")).strip()
    except httpx.HTTPError as exc:
        raise OllamaServiceError(f"Ollama request failed: {exc}") from exc

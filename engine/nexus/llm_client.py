# -*- coding: utf-8 -*-
"""Cliente LLM con contrato JSON estricto.

Principio 4 del blueprint: si el modelo no devuelve JSON válido tras los
reintentos, el pipeline FALLA con error visible. Prohibido el fallback
silencioso que disfraza una falla de API como 'HU sin gaps'.
"""
import json
import time

from nexus import NexusPipelineError
from nexus.config import get_api_key, get_model

SYSTEM_JSON = (
    "Eres un motor de análisis del QASL Shift-Left Testing Framework. "
    "Respondes ÚNICAMENTE con JSON válido, sin texto adicional ni bloques markdown. "
    "REGLA SAGRADA: nunca inventas información que no esté en la fuente; "
    "lo ausente se marca NO_ESPECIFICADO y todo valor que propongas se marca [PROPUESTO]."
)


class LLMClient:
    def __init__(self, model: str = None):
        import anthropic  # import perezoso: los tests offline no lo requieren
        self.client = anthropic.Anthropic(api_key=get_api_key())
        self.model = model or get_model()

    def call_json(self, etapa: str, prompt: str, max_tokens: int = 8000,
                  reintentos: int = 3) -> dict:
        """Llama al modelo exigiendo JSON. Reintenta con feedback del error."""
        ultimo_error = ""
        for intento in range(1, reintentos + 1):
            mensaje = prompt if intento == 1 else (
                prompt
                + "\n\nATENCIÓN: tu respuesta anterior no fue JSON válido "
                + f"({ultimo_error}). Responde SOLO el objeto JSON, completo y bien formado."
            )
            t0 = time.time()
            print(f"      [{etapa}] intento {intento}/{reintentos} — esperando respuesta "
                  f"del modelo (máx {max_tokens} tokens, puede tardar varios minutos)...",
                  flush=True)
            try:
                resp = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=SYSTEM_JSON,
                    messages=[{"role": "user", "content": mensaje}],
                    timeout=600.0,
                )
                uso = getattr(resp, "usage", None)
                print(f"      [{etapa}] respuesta recibida en {time.time()-t0:.0f}s"
                      + (f" · {uso.output_tokens} tokens generados" if uso else ""),
                      flush=True)
            except Exception as e:  # error de API (red, auth, rate limit, timeout)
                ultimo_error = f"API error: {e}"
                print(f"      [{etapa}] error de API en intento {intento}: {e}", flush=True)
                if intento < reintentos:
                    time.sleep(2 * intento)
                    continue
                raise NexusPipelineError(etapa, f"Falla de API tras {reintentos} intentos: {e}")

            texto = resp.content[0].text.strip()
            texto = self._strip_fences(texto)
            try:
                return json.loads(texto)
            except json.JSONDecodeError as e:
                ultimo_error = f"JSON inválido: {e}"
                if resp.stop_reason == "max_tokens":
                    ultimo_error += " (respuesta truncada por max_tokens)"
                    max_tokens = min(max_tokens * 2, 32000)  # techo real de salida
                print(f"      [{etapa}] {ultimo_error} — reintentando con feedback...", flush=True)

        raise NexusPipelineError(
            etapa,
            f"El modelo no produjo JSON válido tras {reintentos} intentos. Último error: {ultimo_error}"
        )

    @staticmethod
    def _strip_fences(texto: str) -> str:
        if texto.startswith("```"):
            # ```json\n...\n``` o ```\n...\n```
            partes = texto.split("```")
            if len(partes) >= 2:
                cuerpo = partes[1]
                if cuerpo.lower().startswith("json"):
                    cuerpo = cuerpo[4:]
                return cuerpo.strip()
        return texto

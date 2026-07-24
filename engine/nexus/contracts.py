# -*- coding: utf-8 -*-
"""Validación de contratos JSON entre etapas (principio 4 del blueprint)."""
import json
from functools import lru_cache

from jsonschema import Draft202012Validator

from nexus import NexusPipelineError
from nexus.config import SCHEMAS_DIR

_SCHEMAS = {
    "hu_canonica": "hu_canonica.schema.json",
    "certificacion": "certificacion.schema.json",
    "cobertura": "cobertura.schema.json",
    "activos": "activos.schema.json",
}


@lru_cache(maxsize=None)
def _load_schema(nombre: str) -> dict:
    ruta = SCHEMAS_DIR / _SCHEMAS[nombre]
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(nombre: str, data: dict, etapa: str) -> dict:
    """Valida `data` contra el schema `nombre`. Falla ruidosamente si no cumple."""
    schema = _load_schema(nombre)
    validator = Draft202012Validator(schema)
    errores = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errores:
        detalle = "; ".join(
            f"{'/'.join(str(p) for p in e.path) or '<raíz>'}: {e.message}" for e in errores[:5]
        )
        extra = f" (+{len(errores)-5} más)" if len(errores) > 5 else ""
        raise NexusPipelineError(etapa, f"Contrato '{nombre}' violado: {detalle}{extra}")
    return data

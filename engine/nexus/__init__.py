# -*- coding: utf-8 -*-
"""NEXUS Requirements — motor del QASL Shift-Left Testing Framework.

El framework define la norma; NEXUS la ejecuta; el ecosistema la consume.
"""
__version__ = "1.0.0"


class NexusPipelineError(Exception):
    """Falla dura del pipeline. NUNCA se degrada a un resultado vacío
    disfrazado de análisis válido (principio 4 del blueprint)."""
    def __init__(self, etapa: str, mensaje: str):
        self.etapa = etapa
        self.mensaje = mensaje
        super().__init__(f"[{etapa}] {mensaje}")

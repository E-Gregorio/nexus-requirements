# -*- coding: utf-8 -*-
"""Configuración y rutas del motor NEXUS."""
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# engine/ está dentro de nexus-requirements/
ENGINE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = ENGINE_DIR.parent                     # nexus-requirements/
CATALOG_DIR = ROOT_DIR / "catalog"
SCHEMAS_DIR = ROOT_DIR / "schemas"
OUTPUTS_DIR = ROOT_DIR / "outputs"

NX_RULES_FILE = CATALOG_DIR / "nx_rules.yaml"
VCR_POLICY_FILE = CATALOG_DIR / "vcr_policy.yaml"
ID_REGISTRY_FILE = CATALOG_DIR / "id_registry.json"


def load_env():
    """Carga .env desde engine/ (o el cwd) sin pisar variables ya definidas."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ENGINE_DIR / ".env")
        load_dotenv()  # fallback cwd
    except ImportError:
        pass


def get_model() -> str:
    return os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")


def get_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        from nexus import NexusPipelineError
        raise NexusPipelineError(
            "config",
            "ANTHROPIC_API_KEY no definida. Copiar engine/.env.example a engine/.env y completar."
        )
    return key

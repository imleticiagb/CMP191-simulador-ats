"""Logging que registra só metadados (etapa, duração, tamanhos, hash), nunca texto de currículo ou vaga."""

from __future__ import annotations

import hashlib
import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager

LOGGER_NAME = "ats"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def short_hash(text: str) -> str:
    """Identificador curto e irreversível de um texto, seguro para registrar."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


def log_event(stage: str, **meta: int | float | str | bool) -> None:
    """Registra uma etapa. Só aceita valores simples, para não vazar conteúdo por engano."""
    safe = " ".join(f"{k}={v}" for k, v in sorted(meta.items()))
    get_logger().info("stage=%s %s", stage, safe)


@contextmanager
def timed(stage: str, **meta: int | float | str | bool) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        log_event(stage, duration_ms=int((time.perf_counter() - start) * 1000), **meta)

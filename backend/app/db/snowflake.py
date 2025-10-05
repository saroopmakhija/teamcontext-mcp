from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from snowflake import connector
from snowflake.connector import SnowflakeConnection
from snowflake.connector.errors import Error as SnowflakeError

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SnowflakeState:
    connection: Optional[SnowflakeConnection] = None


db = SnowflakeState()


def _build_connect_kwargs() -> Optional[dict[str, str]]:
    """Prepare connection keyword arguments, ensuring required fields exist."""

    required = {
        "user": settings.snowflake_user,
        "password": settings.snowflake_password,
        "account": settings.snowflake_account,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        logger.info(
            "Skipping Snowflake connection; missing configuration values: %s",
            ", ".join(missing),
        )
        return None

    optional = {
        "database": settings.snowflake_database,
        "schema": settings.snowflake_schema,
        "role": settings.snowflake_role,
        "authenticator": "snowflake"
    }

    kwargs = {**required, **{k: v for k, v in optional.items() if v}}
    return kwargs


async def connect_to_snowflake() -> None:
    """Establish a Snowflake connection and cache it on the module state."""

    if db.connection and not db.connection.is_closed():
        return

    kwargs = _build_connect_kwargs()
    if not kwargs:
        return

    def _connect() -> SnowflakeConnection:
        return connector.connect(**kwargs)

    try:
        db.connection = await asyncio.to_thread(_connect)
        location = kwargs.get("database") or "account"
        if kwargs.get("schema"):
            location = f"{location}.{kwargs['schema']}" if location else kwargs["schema"]
        logger.info("Connected to Snowflake %s", location)
    except SnowflakeError as error:
        logger.error("Failed to connect to Snowflake: %s", error)
        db.connection = None
    except Exception as error:  # pragma: no cover - defensive fallback
        logger.exception("Unexpected error when connecting to Snowflake")
        db.connection = None


async def close_snowflake_connection() -> None:
    """Close the Snowflake connection if it was previously opened."""

    connection = db.connection
    if not connection:
        return

    def _close() -> None:
        if not connection.is_closed():
            connection.close()

    await asyncio.to_thread(_close)
    db.connection = None
    logger.info("Closed Snowflake connection")


def get_snowflake_connection() -> SnowflakeConnection:
    """Return the active Snowflake connection or raise if unavailable."""

    if not db.connection or db.connection.is_closed():
        raise RuntimeError("Snowflake connection has not been initialized")
    return db.connection

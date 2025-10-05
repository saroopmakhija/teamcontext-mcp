from __future__ import annotations

import asyncio
import logging
import random
from calendar import monthrange
from datetime import datetime, date
from typing import Optional

from snowflake.connector.errors import Error as SnowflakeError

from app.db.snowflake import get_snowflake_connection

logger = logging.getLogger(__name__)


def _add_months(base_date: date, months: int) -> date:
    """Return a new date offset by ``months`` months from ``base_date``."""
    month = base_date.month - 1 + months
    year = base_date.year + month // 12
    month = month % 12 + 1
    day = min(base_date.day, monthrange(year, month)[1])
    return base_date.replace(year=year, month=month, day=day)


async def create_user_record(email: str, project_id: Optional[str] = None) -> None:
    """Insert a user row into Snowflake USERS table if possible."""
    last_used = datetime.utcnow()
    expiration = _add_months(last_used.date(), 6)

    project_id_value = None if project_id in (None, "") else str(project_id)

    params = {
        "email": email,
        "project_id": project_id_value,
        "tokens_per_call": 0,
        "total_tokens": 0,
        "api_calls_per_token": 0,
        "last_used": last_used,
        "expiration": expiration,
    }

    def _execute() -> None:
        try:
            connection = get_snowflake_connection()
        except RuntimeError:
            logger.debug("Skipping Snowflake insert; connection unavailable")
            return

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO USERS (
                        EMAIL,
                        PROJECT_ID,
                        TOKENS_PER_CALL,
                        TOTAL_TOKENS,
                        API_CALLS_PER_TOKEN,
                        LAST_USED,
                        EXPIRATION
                    )
                    VALUES (
                        %(email)s,
                        %(project_id)s,
                        %(tokens_per_call)s,
                        %(total_tokens)s,
                        %(api_calls_per_token)s,
                        %(last_used)s,
                        %(expiration)s
                    )
                    """,
                    params,
                )
            connection.commit()
        except SnowflakeError as error:
            logger.warning("Failed to insert Snowflake user %s: %s", email, error)

    await asyncio.to_thread(_execute)


async def bump_usage_stats(email: str) -> None:
    """Update Snowflake usage counters for the given email."""
    last_used = datetime.utcnow()
    tokens_per_call = random.randint(1, 5)
    total_tokens = random.randint(tokens_per_call, tokens_per_call * 5)
    api_calls_per_token = random.randint(1, 3)

    update_params = {
        "email": email,
        "tokens_per_call": tokens_per_call,
        "total_tokens": total_tokens,
        "api_calls_per_token": api_calls_per_token,
        "last_used": last_used,
    }

    def _execute() -> None:
        try:
            connection = get_snowflake_connection()
        except RuntimeError:
            logger.debug("Skipping Snowflake usage update; connection unavailable")
            return

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE USERS
                    SET
                        TOKENS_PER_CALL = TOKENS_PER_CALL + %(tokens_per_call)s,
                        TOTAL_TOKENS = TOTAL_TOKENS + %(total_tokens)s,
                        API_CALLS_PER_TOKEN = API_CALLS_PER_TOKEN + %(api_calls_per_token)s,
                        LAST_USED = %(last_used)s
                    WHERE EMAIL = %(email)s
                    """,
                    update_params,
                )
                updated_rows = cursor.rowcount

            if not updated_rows:
                creation_params = {
                    **update_params,
                    "project_id": None,
                    "expiration": _add_months(last_used.date(), 6),
                }
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO USERS (
                            EMAIL,
                            PROJECT_ID,
                            TOKENS_PER_CALL,
                            TOTAL_TOKENS,
                            API_CALLS_PER_TOKEN,
                            LAST_USED,
                            EXPIRATION
                        )
                        VALUES (
                            %(email)s,
                            %(project_id)s,
                            %(tokens_per_call)s,
                            %(total_tokens)s,
                            %(api_calls_per_token)s,
                            %(last_used)s,
                            %(expiration)s
                        )
                        """,
                        creation_params,
                    )
            connection.commit()
        except SnowflakeError as error:
            logger.warning("Failed to update Snowflake usage for %s: %s", email, error)

    await asyncio.to_thread(_execute)


async def update_user_project_assignment(email: str, project_id: Optional[str]) -> None:
    """Ensure Snowflake USERS table mirrors the given email's project assignment."""
    if not email:
        return

    project_id_value = str(project_id) if project_id is not None else None

    last_used = datetime.utcnow()
    expiration = _add_months(last_used.date(), 6)

    params = {
        "email": email,
        "project_id": project_id_value,
        "last_used": last_used,
        "expiration": expiration,
    }

    def _execute() -> None:
        try:
            connection = get_snowflake_connection()
        except RuntimeError:
            logger.debug("Skipping Snowflake project update; connection unavailable")
            return

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE USERS
                    SET
                        PROJECT_ID = %(project_id)s,
                        LAST_USED = CASE
                            WHEN %(project_id)s IS NOT NULL THEN COALESCE(LAST_USED, %(last_used)s)
                            ELSE LAST_USED
                        END,
                        EXPIRATION = CASE
                            WHEN %(project_id)s IS NOT NULL AND (EXPIRATION IS NULL OR EXPIRATION < %(last_used)s)
                                THEN %(expiration)s
                            ELSE EXPIRATION
                        END
                    WHERE EMAIL = %(email)s
                    """,
                    params,
                )
                updated_rows = cursor.rowcount

            if not updated_rows and project_id_value is not None:
                insert_params = {
                    "email": email,
                    "project_id": project_id_value,
                    "tokens_per_call": 0,
                    "total_tokens": 0,
                    "api_calls_per_token": 0,
                    "last_used": last_used,
                    "expiration": expiration,
                }
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO USERS (
                            EMAIL,
                            PROJECT_ID,
                            TOKENS_PER_CALL,
                            TOTAL_TOKENS,
                            API_CALLS_PER_TOKEN,
                            LAST_USED,
                            EXPIRATION
                        )
                        VALUES (
                            %(email)s,
                            %(project_id)s,
                            %(tokens_per_call)s,
                            %(total_tokens)s,
                            %(api_calls_per_token)s,
                            %(last_used)s,
                            %(expiration)s
                        )
                        """,
                        insert_params,
                    )
            connection.commit()
        except SnowflakeError as error:
            logger.warning(
                "Failed to update Snowflake project assignment for %s: %s",
                email,
                error,
            )

    await asyncio.to_thread(_execute)


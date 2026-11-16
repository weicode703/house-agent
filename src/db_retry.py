import logging
import time
from typing import Any

from sqlalchemy.exc import OperationalError

DATABASE_RETRY_DELAYS = (0.5, 1.0, 2.0)
MYSQL_DISCONNECT_CODES = {2002, 2003, 2006, 2013, 2055}
logger = logging.getLogger(__name__)


def _is_transient_database_disconnect(error: OperationalError) -> bool:
    if error.connection_invalidated:
        return True

    original_error = error.orig
    error_args = getattr(original_error, "args", ())
    error_code = error_args[0] if error_args and isinstance(error_args[0], int) else None
    return error_code in MYSQL_DISCONNECT_CODES


def invoke_database_tool_with_retry(tool: Any, tool_input: dict[str, Any]) -> Any:
    max_attempts = len(DATABASE_RETRY_DELAYS) + 1
    for attempt in range(1, max_attempts + 1):
        try:
            return tool.invoke(tool_input)
        except OperationalError as error:
            if not _is_transient_database_disconnect(error) or attempt == max_attempts:
                raise

            delay = DATABASE_RETRY_DELAYS[attempt - 1]
            logger.warning(
                "MySQL connection dropped during %s; retry %d/%d in %.1f seconds",
                tool.name,
                attempt,
                len(DATABASE_RETRY_DELAYS),
                delay,
            )
            time.sleep(delay)

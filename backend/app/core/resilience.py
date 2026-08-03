import concurrent.futures

from app.core.config import TOOL_RETRY_LIMIT, TOOL_TIMEOUT_SECONDS


def call_with_timeout(fn, *args, timeout=TOOL_TIMEOUT_SECONDS, retries=TOOL_RETRY_LIMIT, **kwargs):
    """Run fn in a worker thread, retrying on timeout/error up to `retries` times"""
    last_error = None
    for _ in range(retries + 1):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(fn, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except Exception as e:
                last_error = e
    raise last_error

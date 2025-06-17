
def startup_sync_not_implemented() -> None:
    """
    Start synchronous web server: gunicorn + Flask (default sync)
    """
    import sys
    import logging
    msg = (
        " Synchronous startup is not implemented yet. "
        "Please use the fastapi web_api adapter."
    )
    logging.warning(msg)
    sys.exit(1)
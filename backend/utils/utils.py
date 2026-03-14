


def logger():
    import logging
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    return log

def get_today_date() -> str:
    """Get the current date in YYYY-MM-DD format"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d")
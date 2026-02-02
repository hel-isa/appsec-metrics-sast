import os
import logging
def configure_logging():
level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.getLogger().setLevel(level)

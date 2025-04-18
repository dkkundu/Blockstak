import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


# Custom handler to rename the rotated file with date prefix
class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        super().doRollover()

        # Rename the most recent backup file
        base_filename = self.baseFilename
        current_date = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(base_filename + ".1"):
            new_name = os.path.join(LOG_DIR, f"{current_date}_{os.path.basename(base_filename)}")
            os.rename(base_filename + ".1", new_name)


# Helper to create a handler per level
def create_handler(log_level, filename):
    handler = CustomTimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, filename),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8',
        delay=False
    )
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    return handler


# Create separate handlers with base file names
info_handler = create_handler(logging.INFO, "info.log")
debug_handler = create_handler(logging.DEBUG, "debug.log")
error_handler = create_handler(logging.ERROR, "error.log")

# Root logger setup
logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.DEBUG)

# Filter handlers to their levels
info_handler.addFilter(lambda record: record.levelno == logging.INFO)
debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)

# Add handlers
logger.addHandler(info_handler)
logger.addHandler(debug_handler)
logger.addHandler(error_handler)

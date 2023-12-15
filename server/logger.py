import logging
logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.propagate = True

# ANSI escape codes for coloring
COLORS = {
    logging.DEBUG: "\033[94m",      # Blue
    logging.INFO: "\033[92m",       # Green
    logging.WARNING: "\033[93m",    # Yellow
    logging.ERROR: "\033[91m",      # Red
    logging.CRITICAL: "\033[95m",   # Magenta
    "reset": "\033[0m",             # Reset color
}
from typing import Literal
log_type =  logging.NOTSET | logging.DEBUG | logging.INFO  |   logging.WARNING | logging.ERROR | logging.CRITICAL 
def log(message, level=logging.INFO):
    global logger
    
    # Apply color to the log message
    colored_message = f"{COLORS.get(level, COLORS['reset'])}{message}{COLORS['reset']}"
    
    logger.log(level, colored_message)

if __name__ == "__main__":
    log("This is a debug message", level=logging.DEBUG)
    log("This is an info message", level= logging.INFO)
    log("This is a warning message", level=logging.WARNING)
    log("This is an error message", level=logging.ERROR)
    log("This is a critical message", level=logging.CRITICAL)
    log("Invalid log level", level=15)
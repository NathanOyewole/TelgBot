# src/utils/logger.py
import logging
import sys

def setup_logger():
    """
    Configures and returns a logger instance for the application.
    """
    logger = logging.getLogger("TelgBot") # Give your logger a specific name
    logger.setLevel(logging.INFO) # Set the default logging level to INFO

    # Create a stream handler to output logs to the console
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO) # Console output will show INFO and above

    # Define the log message format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    stream_handler.setFormatter(formatter)

    # Add the handler to the logger
    # This check prevents adding duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        logger.addHandler(stream_handler)

    return logger

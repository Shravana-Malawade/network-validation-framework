"""
Logger Module

This module is responsible for configuring and creating
the logger used throughout the Network Validation Framework.
"""

import logging
import os


def setup_logger(config):
    """
    Configure and create the framework logger.

    Args:
        config (dict): Configuration dictionary loaded from config.yaml.

    Returns:
        logging.Logger: Configured logger object.
    """

    # Get logging configuration from config dictionary
    logging_config = config["logging"]

    # Create logger object
    logger = logging.getLogger("NetworkValidationFramework")

    # Convert log level string (INFO, ERROR, etc.) to logging constant
    log_level = getattr(logging, logging_config["level"])

    # Set logger level
    logger.setLevel(log_level)

    # Get log file path from configuration
    log_path = logging_config["path"]

    # Get the parent directory of the log file
    log_directory = os.path.dirname(log_path)

    # Create the log directory if it does not already exist
    if log_directory:
        os.makedirs(log_directory, exist_ok=True)

    # Create file handler
    file_handler = logging.FileHandler(log_path)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Attach formatter to file handler
    file_handler.setFormatter(formatter)

    # Attach file handler to logger
    if not logger.handlers:
        logger.addHandler(file_handler)

    # Return configured logger object
    return logger

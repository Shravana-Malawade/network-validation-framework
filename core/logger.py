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

    # Convert log level string to logging constant
    log_level = getattr(
        logging,
        logging_config["level"].upper()
    )

    # Set logger level
    logger.setLevel(log_level)

    # Get configured log file path
    log_path = logging_config["path"]

    # Create log directory automatically if it does not exist
    log_directory = os.path.dirname(log_path)

    if log_directory:
        os.makedirs(
            log_directory,
            exist_ok=True
        )

    # Create file handler
    file_handler = logging.FileHandler(
        log_path
    )

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Attach formatter to file handler
    file_handler.setFormatter(formatter)

    # Attach file handler only once
    if not logger.handlers:
        logger.addHandler(file_handler)

    # Return configured logger object
    return logger

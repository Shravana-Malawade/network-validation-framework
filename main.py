"""
Main entry point for the Network Validation Framework.
"""

from utils.config_loader import load_config
from core.logger import setup_logger


def main():
    """
    Main function of the framework.
    """

    # Load configuration
    config = load_config()

    # Configure logger
    logger = setup_logger(config)

    # Test log messages
    logger.info("Framework Started Successfully")
    logger.info("Configuration Loaded Successfully")

    print("Framework executed successfully.")


if __name__ == "__main__":
    main()

"""
Main entry point for the Network Validation Framework.
"""

from utils.config_loader import load_config
from core.logger import setup_logger
from core.ssh import connect_ssh


def main():
    """
    Main function of the framework.
    """
    
    # Load configuration
    config = load_config()
    
    # Configure logger
    logger = setup_logger(config)
    
    # Framework startup logs
    logger.info("Framework Started Successfully")
    logger.info("Configuration Loaded Successfully")
    
    # Establish SSH connection
    ssh = connect_ssh(config, logger)

    # Check whether SSH connection was successful
    if ssh is None:
        logger.error("Framework stopped because SSH connection failed.")
        return

    print("Framework executed successfully.")


if __name__ == "__main__":
    main()

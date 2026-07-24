"""
Main entry point for the Network Validation Framework.
"""

from utils.config_loader import load_config
from core.logger import setup_logger
from core.ssh import connect_ssh
from core.command import execute_command


def main():
    """
    Main function of the framework.
    """

    # Load configuration from YAML file
    config = load_config()

    # Create logger object
    logger = setup_logger(config)

    # Framework startup logs
    logger.info("Framework Started Successfully")
    logger.info("Configuration Loaded Successfully")

    # Establish SSH connection with DUT
    ssh = connect_ssh(config, logger)

    # Check SSH connection status
    if ssh is None:
        logger.error(
            "Framework stopped because SSH connection failed."
        )
        return

    # Execute Linux command on DUT
    output = execute_command(
        ssh,
        "hostname",
        logger
    )

    # Check command execution result
    if output is not None:
        print("Command Output:")
        print(output)

    else:
        logger.error(
            "Command execution failed."
        )

    # Close SSH connection after execution
    ssh.close()

    logger.info("SSH connection closed successfully.")

    print("Framework executed successfully.")


if __name__ == "__main__":
    main()

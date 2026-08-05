"""
Main entry point for the Network Validation Framework.
"""

import argparse

from utils.config_loader import load_config
from core.logger import setup_logger
from core.ssh import connect_ssh
from core.test_runner import run_tests
from core.reporter import generate_report


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace:
            User provided framework options.
    """

    parser = argparse.ArgumentParser(
        description="Network Validation Framework"
    )

    parser.add_argument(
        "--suite",
        default="all",
        help="Test suite to execute"
    )

    return parser.parse_args()



def main():
    """
    Main function of the framework.

    Flow:
        1. Parse command line arguments
        2. Load framework configuration
        3. Setup logger
        4. Connect to DUT through SSH
        5. Execute validation test cases
        6. Generate report
        7. Close SSH connection
    """


    # Read command line arguments
    args = parse_arguments()


    # Load configuration from config.yaml
    config = load_config()


    # Initialize logger
    logger = setup_logger(config)

    logger.info("Framework Started Successfully")
    logger.info("Configuration Loaded Successfully")


    # Establish SSH connection with DUT
    ssh = connect_ssh(
        config,
        logger
    )


    # Stop execution if SSH connection fails
    if ssh is None:

        logger.error(
            "Framework stopped because SSH connection failed."
        )

        return


    # Execute validation test cases
    results = run_tests(
        ssh,
        config,
        logger,
        args.suite
    )


    # Display validation results
    generate_report(
        results,
        config
    )


    # Close SSH connection
    ssh.close()


    logger.info(
        "SSH connection closed successfully."
    )


    print(
        "Framework executed successfully."
    )


if __name__ == "__main__":
    main()

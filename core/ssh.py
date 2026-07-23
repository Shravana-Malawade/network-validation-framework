"""
SSH Connection Module

This module is responsible for establishing and managing
SSH connections to the Device Under Test (DUT).
"""

import paramiko


def connect_ssh(config, logger):
    """
    Establish an SSH connection to the active device.

    Args:
        config (dict): Configuration dictionary loaded from config.yaml.
        logger (logging.Logger): Logger object used for logging messages.

    Returns:
        paramiko.SSHClient: Connected SSH client object.
        None: If the connection fails.
    """

    # Get the active device name
    active_device = config["active_device"]

    # Read the active device configuration
    device = config["devices"][active_device]

    # Extract SSH credentials
    host = device["host"]
    username = device["username"]
    password = device["password"]

    # Create SSH client object
    ssh_client = paramiko.SSHClient()

    try:
        # Automatically accept unknown host keys
        ssh_client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        # Establish SSH connection
        ssh_client.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=10
        )

        logger.info("SSH connection established successfully.")

        return ssh_client

    except Exception as error:
        logger.error(f"SSH connection failed: {error}")

        return None

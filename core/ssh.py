"""
SSH Connection Module

Responsible for establishing and managing
SSH connections to configured DUTs.
"""

import paramiko


def connect_device_ssh(device, logger):
    """
    Establish an SSH connection to a specific device configuration.

    Args:
        device:
            Device configuration dictionary.

        logger:
            Framework logger.

    Returns:
        paramiko.SSHClient:
            Connected SSH client.

        None:
            If connection fails.
    """

    host = device["host"]
    username = device["username"]
    password = device["password"]

    ssh_client = paramiko.SSHClient()

    try:
        ssh_client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        ssh_client.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=10
        )

        logger.info(
            f"SSH connection established successfully: {host}"
        )

        return ssh_client

    except Exception as error:
        logger.error(
            f"SSH connection failed to {host}: {error}"
        )

        return None


def connect_ssh(config, logger):
    """
    Establish an SSH connection to the active DUT.

    Args:
        config:
            Framework configuration.

        logger:
            Framework logger.

    Returns:
        paramiko.SSHClient:
            Connected SSH client.

        None:
            If connection fails.
    """

    active_device = config["active_device"]

    device = config["devices"][active_device]

    return connect_device_ssh(
        device,
        logger
    )

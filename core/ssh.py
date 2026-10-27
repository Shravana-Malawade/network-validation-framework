"""
SSH Connection Module

Establishes and manages SSH connections
to validation devices.
"""

import paramiko


def connect_device(config, device_name, logger):
    """
    Establish SSH connection to a specific configured device.
    """

    device = config["devices"][device_name]

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
            f"SSH connection established to "
            f"{device_name} ({host})"
        )

        return ssh_client

    except Exception as error:
        logger.error(
            f"SSH connection failed to "
            f"{device_name} ({host}): {error}"
        )

        return None


def connect_ssh(config, logger):
    """
    Connect to the configured active DUT.

    This keeps the existing framework behavior unchanged.
    """

    active_device = config["active_device"]

    return connect_device(
        config,
        active_device,
        logger
    )

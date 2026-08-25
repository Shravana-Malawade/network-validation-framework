"""
Layer 3 Ping Validation Module

Contains validations for:
1. Default gateway reachability
2. Bidirectional peer DUT reachability
"""

from core.ssh import connect_device_ssh


def validate_ping(ssh, test_case, logger):
    """
    Validate default gateway reachability.

    Args:
        ssh:
            Active SSH connection to DUT.

        test_case:
            Test case dictionary.

        logger:
            Framework logger.

    Returns:
        dict:
            Validation result.
    """

    logger.info(
        "Starting default gateway reachability validation"
    )

    # Get configured default gateway
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $3}'"
    )

    gateway = stdout.read().decode().strip()

    if gateway == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Default gateway not configured"
        }

    logger.info(
        f"Detected Default Gateway : {gateway}"
    )

    # Ping gateway using 4 ICMP packets
    stdin, stdout, stderr = ssh.exec_command(
        f"ping -c 4 -W 2 {gateway}"
    )

    stdout.read()

    exit_status = stdout.channel.recv_exit_status()

    if exit_status == 0:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
            f"Default gateway reachable: {gateway}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
        f"Default gateway unreachable: {gateway}"
    }


def validate_peer_ping(ssh, test_case, logger, config):
    """
    Validate bidirectional reachability between
    the active DUT and another configured peer DUT.

    Args:
        ssh:
            Active SSH connection to the active DUT.

        test_case:
            Test case dictionary.

        logger:
            Framework logger.

        config:
            Framework configuration.

    Returns:
        dict:
            Validation result.
    """

    logger.info(
        "Starting peer DUT reachability validation"
    )

    active_device_name = config["active_device"]
    devices = config["devices"]

    active_device = devices[active_device_name]

    # Find another configured device to use as peer
    peer_device_name = None

    for device_name in devices:
        if device_name != active_device_name:
            peer_device_name = device_name
            break

    if peer_device_name is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Peer DUT is not configured"
        }

    peer_device = devices[peer_device_name]

    active_host = active_device["host"]
    peer_host = peer_device["host"]

    logger.info(
        f"Active DUT : {active_device_name} ({active_host})"
    )

    logger.info(
        f"Peer DUT : {peer_device_name} ({peer_host})"
    )

    # Direction 1:
    # Active DUT -> Peer DUT
    stdin, stdout, stderr = ssh.exec_command(
        f"ping -c 4 -W 2 {peer_host}"
    )

    stdout.read()

    active_to_peer_status = (
        stdout.channel.recv_exit_status()
    )

    if active_to_peer_status != 0:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
            f"Peer DUT unreachable: "
            f"{active_host} -> {peer_host}"
        }

    logger.info(
        f"Reachability passed: {active_host} -> {peer_host}"
    )

    # Establish SSH connection to peer DUT
    peer_ssh = connect_device_ssh(
        peer_device,
        logger
    )

    if peer_ssh is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
            f"Unable to establish SSH connection "
            f"to peer DUT: {peer_host}"
        }

    try:
        # Direction 2:
        # Peer DUT -> Active DUT
        stdin, stdout, stderr = peer_ssh.exec_command(
            f"ping -c 4 -W 2 {active_host}"
        )

        stdout.read()

        peer_to_active_status = (
            stdout.channel.recv_exit_status()
        )

    finally:
        peer_ssh.close()

    if peer_to_active_status != 0:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
            f"Reverse peer reachability failed: "
            f"{peer_host} -> {active_host}"
        }

    logger.info(
        f"Reachability passed: {peer_host} -> {active_host}"
    )

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "PASS",
        "remarks":
        f"Bidirectional peer reachability verified: "
        f"{active_host} <-> {peer_host}"
    }

"""
TCP Peer Connectivity Validation Module

Validates TCP connection establishment
from the active DUT to a configured peer DUT.
"""


def validate_tcp(ssh, test_case, logger, config):
    """
    Validate TCP connection establishment
    from the active DUT to the peer DUT.

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
        "Starting TCP peer connectivity validation"
    )

    active_device_name = config["active_device"]
    devices = config["devices"]

    active_device = devices[active_device_name]

    # Find another configured DUT to use as peer
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

    # Read TCP port from test case.
    # Default to SSH port 22 if not provided.
    port = test_case.get("port", 22)

    logger.info(
        f"Testing TCP connection: "
        f"{active_host} -> {peer_host}:{port}"
    )

    command = (
        f"timeout 5 bash -c "
        f"'cat < /dev/null > /dev/tcp/{peer_host}/{port}'"
    )

    stdin, stdout, stderr = ssh.exec_command(
        command
    )

    # Read command output before obtaining exit status
    stdout.read()

    error = stderr.read().decode().strip()

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
            f"TCP connection successful: "
            f"{active_host} -> {peer_host}:{port}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
        f"TCP connection failed: "
        f"{active_host} -> {peer_host}:{port}. "
        f"{error}"
    }

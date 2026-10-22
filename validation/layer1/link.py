"""
Ethernet Link Validation Module

Validates physical Ethernet link status
and operational state on the Device Under Test.
"""


def validate_link(ssh, test_case, logger):
    """
    Validate physical Ethernet carrier/link status.
    """

    logger.info("Starting Ethernet physical link validation")

    # Detect active Ethernet interface
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $5}'"
    )

    interface = stdout.read().decode().strip()

    if interface == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Network interface not found"
        }

    logger.info(f"Detected Interface : {interface}")

    # Read physical carrier status
    stdin, stdout, stderr = ssh.exec_command(
        f"cat /sys/class/net/{interface}/carrier"
    )

    carrier = stdout.read().decode().strip()

    logger.info(f"Carrier Status : {carrier}")

    if carrier == "1":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"Physical Ethernet link detected on interface: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"Physical Ethernet link not detected on interface: {interface}"
    }


def validate_operstate(ssh, test_case, logger):
    """
    Validate Ethernet interface operational state.
    """

    logger.info("Starting Ethernet operational state validation")

    # Detect active Ethernet interface
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $5}'"
    )

    interface = stdout.read().decode().strip()

    if interface == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Network interface not found"
        }

    logger.info(f"Detected Interface : {interface}")

    # Read operational state
    stdin, stdout, stderr = ssh.exec_command(
        f"cat /sys/class/net/{interface}/operstate"
    )

    operstate = stdout.read().decode().strip()

    logger.info(f"Operational State : {operstate}")

    if operstate == "up":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"Ethernet interface operational state is UP: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"Ethernet interface operational state is: {operstate}"
    }

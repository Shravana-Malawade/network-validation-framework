"""
Ethernet Duplex Validation Module

Validates Ethernet duplex mode
on the Device Under Test.
"""


def validate_duplex(ssh, test_case, logger):
    """
    Validate Ethernet duplex mode.
    """

    logger.info("Starting Ethernet duplex validation")

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

    # Read Ethernet duplex mode
    stdin, stdout, stderr = ssh.exec_command(
        f"cat /sys/class/net/{interface}/duplex"
    )

    duplex = stdout.read().decode().strip().lower()

    logger.info(f"Detected Duplex Mode : {duplex}")

    if duplex == "full":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"Ethernet duplex mode is FULL on interface: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"Unexpected Ethernet duplex mode: {duplex}"
    }

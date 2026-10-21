"""
Ethernet Validation Module

Validates Ethernet interface configuration
on the DUT.
"""


def validate_ethernet(ssh, test_case, logger):
    """
    Validate Ethernet interface MTU.

    Args:
        ssh:
            Active SSH connection.

        test_case:
            Test case dictionary containing test metadata.

        logger:
            Framework logger.

    Returns:
        dict:
            Validation result containing test status and remarks.
    """

    logger.info("Starting Ethernet MTU validation")

    # Detect the active network interface.
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $5}'"
    )

    interface = stdout.read().decode().strip()

    # Fail if an active network interface cannot be detected.
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

    # Read the MTU value from Linux sysfs.
    stdin, stdout, stderr = ssh.exec_command(
        f"cat /sys/class/net/{interface}/mtu"
    )

    mtu_value = stdout.read().decode().strip()

    # Verify that the returned MTU is a valid integer.
    if not mtu_value.isdigit():
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": f"Invalid MTU value: {mtu_value}"
        }

    mtu = int(mtu_value)

    logger.info(f"Detected MTU : {mtu}")

    # Standard Ethernet MTU expected for the current DUT.
    expected_mtu = 1500

    if mtu == expected_mtu:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"Valid Ethernet MTU detected: {mtu} on interface: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"Unexpected Ethernet MTU: {mtu}, expected: {expected_mtu}"
    }

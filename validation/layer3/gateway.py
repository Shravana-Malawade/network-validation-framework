"""
Default Gateway Validation Module

Validates default gateway configuration
on the DUT.
"""

import re


def validate_gateway(ssh, test_case, logger):
    """
    Validate default gateway configuration.

    Args:
        ssh:
            Active SSH connection.

        test_case:
            Test case dictionary.

        logger:
            Framework logger.

    Returns:
        dict:
            Validation result.
    """

    logger.info(
        "Starting default gateway validation"
    )

    # Get default gateway IP
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

    # IPv4 validation pattern
    ip_pattern = (
        r"^(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)$"
    )

    if re.match(ip_pattern, gateway):
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
            f"Valid default gateway detected: {gateway}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
        f"Invalid default gateway detected: {gateway}"
    }

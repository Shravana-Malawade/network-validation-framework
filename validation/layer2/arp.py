"""
ARP Validation Module

Validates Address Resolution Protocol (ARP)
functionality on the DUT.
"""


def validate_arp(ssh, test_case, logger):
    """
    Validate ARP resolution.

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

    logger.info("Starting ARP validation")

    # Get gateway IP
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
            "remarks": "Gateway not found"
        }

    logger.info(f"Gateway IP : {gateway}")

    # Remove old ARP entry
    ssh.exec_command(f"ip neigh del {gateway} dev eth0 >/dev/null 2>&1")

    # Ping gateway to regenerate ARP entry
    ssh.exec_command(f"ping -c 1 {gateway}")

    # Check ARP table
    stdin, stdout, stderr = ssh.exec_command(
        f"ip neigh show {gateway}"
    )

    arp_entry = stdout.read().decode().strip()

    if gateway in arp_entry:

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks": "ARP entry created successfully"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks": "ARP entry not found"
    }

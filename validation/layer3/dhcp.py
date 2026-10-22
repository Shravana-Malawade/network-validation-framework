"""
DHCP Validation Module

Validates dynamic IPv4 address assignment
on the Device Under Test.
"""


def validate_dhcp(ssh, test_case, logger):
    """
    Verify IPv4 address is dynamically assigned through DHCP.
    """

    logger.info("Starting DHCP validation")

    # Detect active Ethernet interface
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | awk '/default/ {print $5; exit}'"
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

    # Read IPv4 address information
    stdin, stdout, stderr = ssh.exec_command(
        f"ip -4 -o addr show dev {interface} scope global"
    )

    output = stdout.read().decode().strip()

    logger.info(f"IPv4 Configuration : {output}")

    if output == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "IPv4 address not assigned"
        }

    if " dynamic " in f" {output} ":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"DHCP/dynamic IPv4 address detected on interface: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"IPv4 address exists but is not marked dynamic on interface: {interface}"
    }

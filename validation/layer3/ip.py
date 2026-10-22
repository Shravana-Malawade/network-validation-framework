"""
IPv4 Address Validation Module

Validates IPv4 address assignment
on the Device Under Test.
"""


def validate_ip(ssh, test_case, logger):
    """
    Validate IPv4 address on active Ethernet interface.
    """

    logger.info("Starting IPv4 address validation")

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

    logger.info(f"Detected Interface : {interface}")

    # Read IPv4 address
    stdin, stdout, stderr = ssh.exec_command(
        f"ip -4 -o addr show dev {interface} scope global"
    )

    output = stdout.read().decode().strip()

    if output == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
                f"No IPv4 address assigned on interface: {interface}"
        }

    parts = output.split()

    try:
        inet_index = parts.index("inet")
        ipv4_address = parts[inet_index + 1]
    except (ValueError, IndexError):
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Unable to parse IPv4 address"
        }

    logger.info(f"Detected IPv4 Address : {ipv4_address}")

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "PASS",
        "remarks":
            f"IPv4 address detected: {ipv4_address} on interface: {interface}"
    }

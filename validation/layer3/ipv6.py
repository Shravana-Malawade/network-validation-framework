"""
IPv6 Validation Module

Validates global and link-local IPv6 addresses
on the Device Under Test.
"""


def _detect_interface(ssh):
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | awk '/default/ {print $5; exit}'"
    )

    return stdout.read().decode().strip()


def validate_ipv6_global(ssh, test_case, logger):
    """
    Validate global IPv6 address.
    """

    logger.info("Starting global IPv6 validation")

    interface = _detect_interface(ssh)

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

    stdin, stdout, stderr = ssh.exec_command(
        f"ip -6 -o addr show dev {interface} scope global"
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
            "remarks": "Global IPv6 address not found"
        }

    parts = output.split()

    try:
        inet6_index = parts.index("inet6")
        ipv6_address = parts[inet6_index + 1]
    except (ValueError, IndexError):
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Unable to parse global IPv6 address"
        }

    logger.info(f"Global IPv6 Address : {ipv6_address}")

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "PASS",
        "remarks":
            f"Global IPv6 address detected: {ipv6_address} "
            f"on interface: {interface}"
    }


def validate_ipv6_link_local(ssh, test_case, logger):
    """
    Validate IPv6 link-local address.
    """

    logger.info("Starting IPv6 link-local validation")

    interface = _detect_interface(ssh)

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

    stdin, stdout, stderr = ssh.exec_command(
        f"ip -6 -o addr show dev {interface} scope link"
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
            "remarks": "IPv6 link-local address not found"
        }

    parts = output.split()

    try:
        inet6_index = parts.index("inet6")
        ipv6_address = parts[inet6_index + 1]
    except (ValueError, IndexError):
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Unable to parse IPv6 link-local address"
        }

    logger.info(f"IPv6 Link-local Address : {ipv6_address}")

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "PASS",
        "remarks":
            f"IPv6 link-local address detected: {ipv6_address} "
            f"on interface: {interface}"
    }

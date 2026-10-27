"""
IP Assignment Mode Validation Module

Validates whether IPv4 configuration is using
DHCP or manual/static addressing.
"""


def validate_dhcp(ssh, test_case, logger):
    """
    Validate IPv4 assignment method against the
    expected method defined in the test case.
    """

    logger.info("Starting IPv4 assignment mode validation")

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

    # Find active NetworkManager connection
    stdin, stdout, stderr = ssh.exec_command(
        f"nmcli -g GENERAL.CONNECTION device show {interface}"
    )

    connection = stdout.read().decode().strip()

    if connection == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Active network connection not found"
        }

    logger.info(f"Connection : {connection}")

    # Read IPv4 assignment method
    stdin, stdout, stderr = ssh.exec_command(
        f'nmcli -g ipv4.method connection show "{connection}"'
    )

    method = stdout.read().decode().strip()

    logger.info(f"IPv4 Method : {method}")

    # NetworkManager uses:
    # auto   = DHCP
    # manual = Static
    if method == "auto":
        detected_assignment = "dynamic"
    elif method == "manual":
        detected_assignment = "manual"
    else:
        detected_assignment = method

    expected_assignment = (
        test_case
        .get("expected", {})
        .get("assignment", "")
    )

    if detected_assignment == expected_assignment:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"IPv4 assignment mode verified as "
                f"{detected_assignment} on interface: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"IPv4 assignment mode is {detected_assignment}, "
            f"expected {expected_assignment}"
    }

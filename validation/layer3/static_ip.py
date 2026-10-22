"""
Static IP Validation Module

Temporarily configures and validates a secondary
IPv4 address without modifying the active DHCP address.
"""


def validate_static_ip(ssh, test_case, logger):
    """
    Add, verify, and remove a temporary static IPv4 address.
    """

    logger.info("Starting temporary static IP validation")

    test_ip = "192.0.2.10/32"

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
    logger.info(f"Temporary Static IP : {test_ip}")

    # Clean up any previous leftover test IP.
    ssh.exec_command(
        f"sudo -n ip addr del {test_ip} dev {interface} 2>/dev/null || true"
    )

    try:
        # Add temporary secondary static IP.
        stdin, stdout, stderr = ssh.exec_command(
            f"sudo -n ip addr add {test_ip} dev {interface}"
        )

        exit_status = stdout.channel.recv_exit_status()
        error = stderr.read().decode().strip()

        if exit_status != 0:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                    f"Failed to configure temporary static IP: {error}"
            }

        # Verify that the address is present.
        stdin, stdout, stderr = ssh.exec_command(
            f"ip -4 -o addr show dev {interface}"
        )

        output = stdout.read().decode().strip()

        logger.info(f"Interface IPv4 Configuration : {output}")

        if test_ip in output:
            result = {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "PASS",
                "remarks":
                    f"Temporary static IP {test_ip} configured and verified "
                    f"on interface: {interface}"
            }
        else:
            result = {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                    f"Temporary static IP {test_ip} was not detected "
                    f"on interface: {interface}"
            }

    finally:
        # Always remove the temporary IP after validation.
        ssh.exec_command(
            f"sudo -n ip addr del {test_ip} dev {interface} 2>/dev/null || true"
        )

        logger.info(
            f"Temporary static IP {test_ip} removed from {interface}"
        )

    return result

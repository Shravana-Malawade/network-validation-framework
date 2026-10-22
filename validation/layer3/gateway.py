"""
Gateway Validation Module

Validates default gateway configuration
on the Device Under Test.
"""


def validate_gateway(ssh, test_case, logger):
    """
    Validate default gateway on active Ethernet interface.
    """

    logger.info("Starting default gateway validation")

    stdin, stdout, stderr = ssh.exec_command(
        "ip route | awk '/default/ {print $3, $5; exit}'"
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
            "remarks": "Default gateway not found"
        }

    parts = output.split()

    if len(parts) < 2:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Unable to parse default gateway"
        }

    gateway = parts[0]
    interface = parts[1]

    logger.info(f"Default Gateway : {gateway}")
    logger.info(f"Gateway Interface : {interface}")

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "PASS",
        "remarks":
            f"Default gateway detected: {gateway} via interface: {interface}"
    }

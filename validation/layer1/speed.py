"""
Ethernet Speed Validation Module

Validates negotiated Ethernet link speed
on the Device Under Test.
"""


def validate_speed(ssh, test_case, logger):
    """
    Validate Ethernet link speed.
    """

    logger.info("Starting Ethernet link speed validation")

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

    stdin, stdout, stderr = ssh.exec_command(
        f"cat /sys/class/net/{interface}/speed"
    )

    speed = stdout.read().decode().strip()

    logger.info(f"Detected Link Speed : {speed} Mbps")

    if speed == "1000":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"Ethernet link speed is 1000 Mbps on interface: {interface}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"Unexpected Ethernet link speed: {speed} Mbps"
    }

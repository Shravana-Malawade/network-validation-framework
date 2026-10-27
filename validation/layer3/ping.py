"""
ICMP Validation Module

Validates network reachability using ICMP ping.
"""


def validate_ping(ssh, test_case, logger):
    """
    Validate ICMP reachability to the default gateway.
    """

    logger.info("Starting ICMP ping validation")

    # Detect default gateway
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | awk '/default/ {print $3; exit}'"
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
            "remarks": "Default gateway not found"
        }

    logger.info(f"Gateway : {gateway}")

    # Ping default gateway
    stdin, stdout, stderr = ssh.exec_command(
        f"ping -c 3 -W 2 {gateway}"
    )

    output = stdout.read().decode().strip()
    exit_status = stdout.channel.recv_exit_status()

    logger.info(f"Ping Output : {output}")

    if exit_status == 0 and "0% packet loss" in output:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"ICMP reachability successful to gateway: {gateway}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"ICMP reachability failed to gateway: {gateway}"
    }

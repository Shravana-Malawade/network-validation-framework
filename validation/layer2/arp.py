"""
ARP Validation Module

Validates IPv4-to-MAC address resolution
for the default gateway on the DUT.
"""


def validate_arp(ssh, test_case, logger):
    """
    Validate ARP/neighbour resolution for default gateway.
    """

    logger.info("Starting ARP validation")

    # Detect default gateway and Ethernet interface
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
            "remarks": "Unable to detect gateway/interface"
        }

    gateway = parts[0]
    interface = parts[1]

    logger.info(f"Gateway : {gateway}")
    logger.info(f"Interface : {interface}")

    # Generate traffic so ARP/neighbour entry is populated
    ssh.exec_command(
        f"ping -c 1 -W 2 {gateway}"
    )

    # Read neighbour/ARP entry
    stdin, stdout, stderr = ssh.exec_command(
        f"ip neigh show {gateway} dev {interface}"
    )

    neighbour = stdout.read().decode().strip()

    logger.info(f"ARP Entry : {neighbour}")

    if neighbour == "":
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
                f"ARP entry not found for gateway: {gateway}"
        }

    if "lladdr" in neighbour and \
            "FAILED" not in neighbour and \
            "INCOMPLETE" not in neighbour:

        mac = neighbour.split("lladdr")[1].split()[0]

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"ARP resolution successful: {gateway} resolved to {mac}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
            f"ARP resolution failed for gateway: {gateway}"
    }

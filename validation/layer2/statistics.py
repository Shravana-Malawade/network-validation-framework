"""
Ethernet Statistics Validation Module

Validates RX/TX packet and byte statistics
of the active network interface on the DUT.
"""


def validate_statistics(ssh, test_case, logger):
    """
    Validate Ethernet interface statistics.

    Args:
        ssh:
            Active SSH connection.

        test_case:
            Test case dictionary containing test metadata.

        logger:
            Framework logger.

    Returns:
        dict:
            Validation result containing test status and remarks.
    """

    logger.info("Starting Ethernet statistics validation")

    # Detect the active network interface.
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $5}'"
    )

    interface = stdout.read().decode().strip()

    # Fail if an active interface cannot be detected.
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

    # Define the statistics that must be available.
    statistics = [
        "rx_packets",
        "tx_packets",
        "rx_bytes",
        "tx_bytes",
        "rx_errors",
        "tx_errors",
        "rx_dropped",
        "tx_dropped"
    ]

    values = {}

    # Read every required network statistic from the DUT.
    for statistic in statistics:

        command = (
            f"cat /sys/class/net/{interface}/statistics/{statistic}"
        )

        stdin, stdout, stderr = ssh.exec_command(command)

        value = stdout.read().decode().strip()

        # Verify that the statistic contains a valid integer.
        if not value.isdigit():

            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                    f"Invalid value for {statistic}: {value}"
            }

        values[statistic] = int(value)

    logger.info(f"RX Packets : {values['rx_packets']}")
    logger.info(f"TX Packets : {values['tx_packets']}")
    logger.info(f"RX Bytes   : {values['rx_bytes']}")
    logger.info(f"TX Bytes   : {values['tx_bytes']}")
    logger.info(f"RX Errors  : {values['rx_errors']}")
    logger.info(f"TX Errors  : {values['tx_errors']}")
    logger.info(f"RX Dropped : {values['rx_dropped']}")
    logger.info(f"TX Dropped : {values['tx_dropped']}")

    # All required statistics were successfully read and validated.
    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "PASS",
        "remarks":
            f"Valid Ethernet statistics detected on interface: {interface}"
    }

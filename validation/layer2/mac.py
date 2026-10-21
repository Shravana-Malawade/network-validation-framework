"""
MAC Address Validation Module

Validates Ethernet MAC address
configuration on the DUT.
"""


import re



def validate_mac(ssh, test_case, logger):
    """
    Validate MAC address of active network interface.

    Args:
        ssh:
            Active SSH connection.

        test_case:
            Test case dictionary.

        logger:
            Framework logger.

    Returns:
        dict:
            Validation result.
    """


    logger.info(
        "Starting MAC address validation"
    )


    # Detect active network interface
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $5}'"
    )


    interface = stdout.read().decode().strip()



    if interface == "":


        return {

            "test_case_id":
            test_case["test_case_id"],

            "category":
            test_case["category"],

            "type":
            test_case["type"],

            "priority":
            test_case["priority"],

            "description":
            test_case["description"],

            "status":
            "FAIL",

            "remarks":
            "Network interface not found"

        }



    logger.info(
        f"Detected Interface : {interface}"
    )



    # Get MAC address from detected interface
    stdin, stdout, stderr = ssh.exec_command(
        f"ip link show {interface} | grep ether"
    )


    output = stdout.read().decode().strip()



    if output == "":


        return {

            "test_case_id":
            test_case["test_case_id"],

            "category":
            test_case["category"],

            "type":
            test_case["type"],

            "priority":
            test_case["priority"],

            "description":
            test_case["description"],

            "status":
            "FAIL",

            "remarks":
            "MAC address not found"

        }



    # Extract MAC address
    mac = output.split()[1]



    logger.info(
        f"Detected MAC Address : {mac}"
    )



    # Validate MAC address format
    mac_pattern = (
        r"^([0-9A-Fa-f]{2}:){5}"
        r"[0-9A-Fa-f]{2}$"
    )



    if re.match(mac_pattern, mac):


        return {

            "test_case_id":
            test_case["test_case_id"],

            "category":
            test_case["category"],

            "type":
            test_case["type"],

            "priority":
            test_case["priority"],

            "description":
            test_case["description"],

            "status":
            "PASS",

            "remarks":
            f"Valid MAC address detected: {mac}"

        }



    return {

        "test_case_id":
        test_case["test_case_id"],

        "category":
        test_case["category"],

        "type":
        test_case["type"],

        "priority":
        test_case["priority"],

        "description":
        test_case["description"],

        "status":
        "FAIL",

        "remarks":
        "Invalid MAC address format"

    }

"""
IP Address Validation Module

Validates IPv4 address configuration
on the DUT.
"""


import re



def validate_ip(ssh, test_case, logger):
    """
    Validate IP address assignment.

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
        "Starting IP address validation"
    )


    # Get IP address of active interface
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



    # Get IP address
    stdin, stdout, stderr = ssh.exec_command(
        f"ip -4 addr show {interface} | grep inet"
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
            "IP address not assigned"

        }



    # Extract IP address
    ip_address = output.split()[1].split("/")[0]


    logger.info(
        f"Detected IP Address : {ip_address}"
    )



    # IPv4 validation pattern
    ip_pattern = (
        r"^(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|"
        r"[01]?[0-9][0-9]?)$"
    )



    if re.match(ip_pattern, ip_address):


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
            f"Valid IPv4 address detected: {ip_address}"

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
        "Invalid IPv4 address format"

    }

"""
TCP Connection Validation Module

Validates TCP connectivity
from the DUT.
"""


import socket



def validate_tcp(ssh, test_case, logger):
    """
    Validate TCP connection.

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
        "Starting TCP connection validation"
    )


    # Test target
    # Using gateway because it is available
    stdin, stdout, stderr = ssh.exec_command(
        "ip route | grep default | awk '{print $3}'"
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
            "remarks": "Gateway not found"

        }



    logger.info(
        f"TCP target : {gateway}"
    )



    # Create TCP connection test command
    command = (
        f"timeout 5 bash -c "
        f"'cat < /dev/null > /dev/tcp/{gateway}/22'"
    )


    stdin, stdout, stderr = ssh.exec_command(
        command
    )


    error = stderr.read().decode().strip()



    if error == "":

        return {

            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks": 
            f"TCP connection successful to {gateway}:22"

        }



    return {

        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
        f"TCP connection failed to {gateway}:22"

    }

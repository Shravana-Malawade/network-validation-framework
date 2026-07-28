"""
Result Management Module

This module is responsible for generating a
standardized validation result.
"""


def generate_result(
    test_case,
    status,
    remarks
):
    """
    Generate a standardized validation result.

    Args:
        test_case (dict):
            Test case information loaded from YAML.

        status (str):
            PASS or FAIL.

        remarks (str):
            Detailed validation result.

    Returns:
        dict:
            Standardized test result.
    """

    result = {

        "test_case_id": test_case["test_case_id"],

        "category": test_case["category"],

        "type": test_case["type"],

        "priority": test_case["priority"],

        "description": test_case["description"],

        "status": status,

        "remarks": remarks
    }

    return result

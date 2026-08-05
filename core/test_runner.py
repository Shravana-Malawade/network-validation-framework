"""
Test Runner Module

Responsible for loading test cases and executing
network validation tests.
"""

import yaml

from core.test_registry import TEST_REGISTRY


def load_test_cases():
    """
    Load validation test cases from YAML file.

    Returns:
        list:
            List of test case dictionaries.
    """

    # Path to layer1 test case file
    test_file = "validation/layer1/test_cases.yaml"

    # Open YAML file and read contents
    with open(test_file, "r") as file:

        # Convert YAML data into Python objects
        test_cases = yaml.safe_load(file)

    return test_cases



def run_tests(ssh, config, logger):
    """
    Execute validation test cases.

    Args:
        ssh:
            Active SSH connection to DUT

        config:
            Framework configuration

        logger:
            Logger object

    Returns:
        list:
            Test execution results
    """

    results = []

    logger.info("Test execution started")


    # Load all test cases
    test_cases = load_test_cases()


    # Execute each test case
    for test_case in test_cases:

        test_id = test_case["test_case_id"]

        logger.info(
            f"Executing test case: {test_id}"
        )


        # Get module name from YAML
        module = test_case["module"]


        # Check whether validation module exists
        if module in TEST_REGISTRY:


            # Get corresponding validation function
            test_function = TEST_REGISTRY[module]


            # Execute validation
            result = test_function(
                ssh,
                test_case,
                logger
            )


            # Store result
            results.append(result)


        else:

            # Module not implemented
            results.append(
                {
                    "test_case_id": test_id,
                    "status": "NOT_SUPPORTED",
                    "message": f"Module {module} is not implemented"
                }
            )


    logger.info(
        "Test execution completed"
    )


    return results

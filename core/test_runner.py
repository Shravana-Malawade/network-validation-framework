"""
Test Runner Module

Responsible for loading test cases and executing
network validation tests.
"""


import yaml

from core.test_registry import TEST_REGISTRY



def load_test_cases(suite):
    """
    Load validation test cases from YAML files.

    Args:
        suite:
            Selected validation suite.

    Returns:
        list:
            Combined list of test case dictionaries.
    """

    test_cases = []


    # Execute all validation suites
    if suite == "all":


        suites = [

            "layer1",
            "layer2",
            "layer3",
            
            "application"

        ]


        # Load test cases from every layer
        for layer in suites:


            test_file = (
                f"validation/{layer}/test_cases.yaml"
            )


            try:


                # Open YAML file
                with open(test_file, "r") as file:


                    # Convert YAML into Python objects
                    cases = yaml.safe_load(file)


                    # Add cases if available
                    if cases:

                        test_cases.extend(cases)



            except FileNotFoundError:


                # Skip layers that are not implemented yet
                print(
                    f"Skipping {layer}: test_cases.yaml not found"
                )



    else:


        # Load selected suite only
        test_file = (
            f"validation/{suite}/test_cases.yaml"
        )


        with open(test_file, "r") as file:


            test_cases = yaml.safe_load(file)



    return test_cases





def run_tests(ssh, config, logger, suite):
    """
    Execute validation test cases.

    Args:
        ssh:
            Active SSH connection to DUT.

        config:
            Framework configuration.

        logger:
            Logger object.

        suite:
            Validation suite selected.

    Returns:
        list:
            Test execution results.
    """


    results = []


    logger.info(
        "Test execution started"
    )



    # Load test cases
    test_cases = load_test_cases(suite)



    # Execute each test case
    for test_case in test_cases:



        test_id = test_case["test_case_id"]



        logger.info(
            f"Executing test case: {test_id}"
        )



        # Get validation module name
        module = test_case["module"]



        # Check whether module is registered
        if module in TEST_REGISTRY:



            # Get validation function
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

                    "message":
                    f"Module {module} is not implemented"

                }

            )



    logger.info(
        "Test execution completed"
    )



    return results

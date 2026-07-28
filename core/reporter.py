"""
Report Generation Module

Responsible for formatting and displaying
network validation test results.
"""


def generate_report(results, config):
    """
    Generate a readable validation report.

    Args:
        results (list):
            List of validation result dictionaries.

        config (dict):
            Framework configuration loaded from config.yaml.

    Returns:
        None
    """

    # Extract framework information
    framework = config["framework"]

    # Extract active device information
    device = config["devices"][config["active_device"]]

    # Count total number of test cases
    total = len(results)

    # Initialize counters
    passed = 0

    failed = 0

    # Print report header
    print("=" * 60)

    print(f"Framework : {framework['name']}")

    print(f"Version   : {framework['version']}")

    print(f"Board     : {device['board']}")

    print(f"IP Address: {device['host']}")

    print("=" * 60)

    # Process each test result
    for result in results:

        # Count PASS and FAIL results
        if result["status"] == "PASS":

            passed += 1

        else:

            failed += 1

        # Print individual test report
        print(f"Test Case ID : {result['test_case_id']}")

        print(f"Category     : {result['category']}")

        print(f"Type         : {result['type']}")

        print(f"Priority     : {result['priority']}")

        print(f"Description  : {result['description']}")

        print(f"Status       : {result['status']}")

        print(f"Remarks      : {result['remarks']}")

        print("-" * 60)

    # Print final summary
    print("Execution Summary")

    print(f"Total Tests : {total}")

    print(f"Passed      : {passed}")

    print(f"Failed      : {failed}")

    print("=" * 60)

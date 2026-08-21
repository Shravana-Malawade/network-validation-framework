"""
Report Generation Module

Responsible for formatting, displaying, and generating
network validation test results.
"""

import os
import xml.etree.ElementTree as ET


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


def generate_junit_report(results, config):
    """
    Generate a JUnit XML report for Jenkins.

    Jenkins can read this report and display individual
    validation test cases with PASS, FAIL, or SKIPPED status.

    Args:
        results (list):
            List of validation result dictionaries.

        config (dict):
            Framework configuration loaded from config.yaml.

    Returns:
        str:
            Path of the generated JUnit XML report.
    """

    # Location where the JUnit report will be generated.
    report_directory = "reports/junit"
    report_path = os.path.join(
        report_directory,
        "network-validation.xml"
    )

    # Create the report directory if it does not already exist.
    os.makedirs(
        report_directory,
        exist_ok=True
    )

    # Count test result types.
    total_tests = len(results)

    failed_tests = sum(
        1
        for result in results
        if result.get("status") == "FAIL"
    )

    skipped_tests = sum(
        1
        for result in results
        if result.get("status") == "NOT_SUPPORTED"
    )

    # Get framework and device information.
    framework = config["framework"]
    device = config["devices"][config["active_device"]]

    # Create the root JUnit test suite.
    test_suite = ET.Element(
        "testsuite",
        {
            "name": framework["name"],
            "tests": str(total_tests),
            "failures": str(failed_tests),
            "skipped": str(skipped_tests)
        }
    )

    # Convert every framework result into a JUnit test case.
    for result in results:

        test_id = result.get(
            "test_case_id",
            "UNKNOWN_TEST"
        )

        category = result.get(
            "category",
            "unknown"
        )

        description = result.get(
            "description",
            ""
        )

        status = result.get(
            "status",
            "FAIL"
        )

        remarks = result.get(
            "remarks",
            result.get("message", "")
        )

        # Create the JUnit test case.
        test_case = ET.SubElement(
            test_suite,
            "testcase",
            {
                "classname": category,
                "name": f"{test_id} - {description}"
            }
        )

        # Add failure information when the test fails.
        if status == "FAIL":

            failure = ET.SubElement(
                test_case,
                "failure",
                {
                    "message": remarks
                }
            )

            failure.text = remarks

        # Mark unsupported tests as skipped.
        elif status == "NOT_SUPPORTED":

            skipped = ET.SubElement(
                test_case,
                "skipped",
                {
                    "message": remarks
                }
            )

            skipped.text = remarks

        # Store remarks for PASS and other results.
        output = ET.SubElement(
            test_case,
            "system-out"
        )

        output.text = remarks

    # Store DUT information inside the test suite.
    properties = ET.SubElement(
        test_suite,
        "properties"
    )

    ET.SubElement(
        properties,
        "property",
        {
            "name": "board",
            "value": str(device["board"])
        }
    )

    ET.SubElement(
        properties,
        "property",
        {
            "name": "host",
            "value": str(device["host"])
        }
    )

    # Format the XML so that it is easy to read.
    tree = ET.ElementTree(test_suite)

    ET.indent(
        tree,
        space="  "
    )

    # Write the XML report to disk.
    tree.write(
        report_path,
        encoding="utf-8",
        xml_declaration=True
    )

    return report_path

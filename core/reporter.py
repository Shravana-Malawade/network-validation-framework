
"""
Report Generation Module

Responsible for displaying validation results
and generating a JUnit XML report for Jenkins.
"""

import os
import xml.etree.ElementTree as ET


def generate_report(results, config):
    """
    Generate console and JUnit XML validation reports.
    """

    framework = config["framework"]
    device = config["devices"][config["active_device"]]

    total = len(results)
    passed = sum(1 for result in results if result.get("status") == "PASS")
    failed = sum(1 for result in results if result.get("status") == "FAIL")
    skipped = total - passed - failed

    # Console report
    print("=" * 60)
    print(f"Framework : {framework['name']}")
    print(f"Version   : {framework['version']}")
    print(f"Board     : {device['board']}")
    print(f"IP Address: {device['host']}")
    print("=" * 60)

    for result in results:
        print(f"Test Case ID : {result.get('test_case_id', 'UNKNOWN')}")
        print(f"Category     : {result.get('category', 'N/A')}")
        print(f"Type         : {result.get('type', 'N/A')}")
        print(f"Priority     : {result.get('priority', 'N/A')}")
        print(f"Description  : {result.get('description', 'N/A')}")
        print(f"Status       : {result.get('status', 'NOT_SUPPORTED')}")
        print(f"Remarks      : {result.get('remarks', result.get('message', 'N/A'))}")
        print("-" * 60)

    print("Execution Summary")
    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Skipped     : {skipped}")
    print("=" * 60)

    # Create JUnit XML report
    report_directory = "reports"
    os.makedirs(report_directory, exist_ok=True)

    test_suite = ET.Element(
        "testsuite",
        name=framework["name"],
        tests=str(total),
        failures=str(failed),
        errors="0",
        skipped=str(skipped)
    )

    for result in results:
        test_id = str(result.get("test_case_id", "UNKNOWN"))

        test_case = ET.SubElement(
            test_suite,
            "testcase",
            name=test_id,
            classname=str(result.get("category", "NetworkValidation"))
        )

        status = result.get("status", "NOT_SUPPORTED")
        remarks = str(
            result.get("remarks", result.get("message", ""))
        )

        if status == "FAIL":
            failure = ET.SubElement(
                test_case,
                "failure",
                message=remarks
            )
            failure.text = remarks

        elif status != "PASS":
            skipped_element = ET.SubElement(
                test_case,
                "skipped",
                message=remarks or status
            )
            skipped_element.text = remarks

        properties = ET.SubElement(test_case, "properties")

        for key in ("description", "type", "priority"):
            value = result.get(key)
            if value is not None:
                ET.SubElement(
                    properties,
                    "property",
                    name=key,
                    value=str(value)
                )

        if remarks:
            system_out = ET.SubElement(test_case, "system-out")
            system_out.text = remarks

    tree = ET.ElementTree(test_suite)
    ET.indent(tree, space="    ")

    report_path = os.path.join(report_directory, "junit.xml")
    tree.write(report_path, encoding="utf-8", xml_declaration=True)

    print(f"JUnit XML report generated: {report_path}")

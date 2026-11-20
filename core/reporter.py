"""Generate console, JUnit XML, and JSON reports for network validation.

JUnit provides test results for Jenkins. JSON records individual outcomes,
timing, and setup failures for use in the detailed validation report.
"""

"""Write console, JUnit XML, and JSON reports for network validation."""

"""Build console, JSON, JUnit, HTML, and DUT network reports."""
"""Generate console, JSON, JUnit, HTML, and DUT network reports."""

import json
import os
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


STATUS_LABELS = (
    "PASS", "FAIL", "ERROR", "BLOCKED", "NOT_SUPPORTED", "SKIPPED", "UNKNOWN",
)

INTERFACE_REMARKS = {
    "Network interface is UP",
    "Command execution failed",
    "No active network interface found",
}

DEFAULT_DETAILS = {
    "PASS": "Validation passed.",
    "FAIL": "Validation failed. See the framework log for diagnostics.",
    "ERROR": "Validation encountered an execution error.",
    "BLOCKED": "Execution was blocked.",
    "NOT_SUPPORTED": "This validation is unsupported.",
    "SKIPPED": "This validation was skipped.",
    "UNKNOWN": "The validator returned an unrecognized status.",
}

RUNNER_DETAILS = {
    "No validator is registered for this test.",
    "Validator raised an unexpected exception.",
    "Execution stopped after a validator error.",
}


def collect_dut_information(ssh):
    """Return live target facts and network details from the DUT over SSH."""
    queries = {
        "Hostname": "hostname",
        "Architecture": "uname -m",
        "Operating system": r"sed -n 's/^PRETTY_NAME=//p' /etc/os-release",
        "Platform": r"tr -d '\000' </proc/device-tree/model",
        "Interfaces": "ip -brief link",
        "Addresses": "ip -brief address",
        "IPv4 routes": "ip -4 route show",
        "IPv6 routes": "ip -6 route show",
    }

    values = {}
    for label, command in queries.items():
        channel = None
        try:
            _, stdout, _ = ssh.exec_command(command, timeout=5)
            channel = stdout.channel
            raw = stdout.read(8193)
            if len(raw) <= 8192 and channel.recv_exit_status() == 0:
                values[label] = raw.decode("utf-8", errors="replace").strip() or None
        except Exception:
            # A diagnostic query can fail independently of the validation suite.
            values[label] = None
        finally:
            if channel is not None:
                channel.close()

    target = {
        key: values.get(key)
        for key in ("Hostname", "Architecture", "Operating system", "Platform")
    }
    if target["Operating system"]:
        target["Operating system"] = target["Operating system"].strip('"')

    network = {
        key: values.get(key)
        for key in ("Interfaces", "Addresses", "IPv4 routes", "IPv6 routes")
    }
    return target, network


def report_test(result):
    """Return the fields and reviewed diagnostic text used in reports."""
    test_id = result.get("test_case_id") or "UNKNOWN"
    status = result.get("status")
    if status not in STATUS_LABELS:
        status = "UNKNOWN"

    # Raw validator errors can contain command output or credentials.
    details = result.get("report_detail")
    remarks = result.get("remarks")
    if isinstance(details, str) and details in RUNNER_DETAILS:
        pass
    elif test_id == "L1_TC_001" and isinstance(remarks, str) and remarks in INTERFACE_REMARKS:
        details = remarks
    else:
        details = DEFAULT_DETAILS[status]

    return {
        "test_case_id": test_id,
        "category": result.get("category"),
        "type": result.get("type"),
        "priority": result.get("priority"),
        "description": result.get("description"),
        "status": status,
        "duration_seconds": result.get("duration_seconds"),
        "remarks": details,
    }


def write_junit(report, path):
    """Write Jenkins-compatible JUnit XML with one entry per test result."""
    counts = report["status_counts"]
    skipped = sum(
        counts.get(status, 0)
        for status in ("BLOCKED", "NOT_SUPPORTED", "SKIPPED")
    )
    suite = ET.Element(
        "testsuite",
        name=str(report["project"]),
        tests=str(report["total_tests"]),
        failures=str(counts.get("FAIL", 0)),
        errors=str(counts.get("ERROR", 0) + counts.get("UNKNOWN", 0)),
        skipped=str(skipped),
    )

    for result in report["tests"]:
        case = ET.SubElement(
            suite,
            "testcase",
            name=str(result["test_case_id"]),
            classname=str(result["category"] or "NetworkValidation"),
        )
        if result["duration_seconds"] is not None:
            case.set("time", f"{result['duration_seconds']:.6f}")

        status = result["status"]
        remarks = result["remarks"]
        if status == "FAIL":
            ET.SubElement(case, "failure", message=remarks).text = remarks
        elif status in ("ERROR", "UNKNOWN"):
            ET.SubElement(case, "error", message=remarks).text = remarks
        elif status in ("BLOCKED", "NOT_SUPPORTED", "SKIPPED"):
            ET.SubElement(case, "skipped", message=remarks).text = status

        properties = ET.SubElement(case, "properties")
        for key in ("description", "type", "priority", "status"):
            if result[key] is not None:
                ET.SubElement(properties, "property", name=key, value=str(result[key]))

        ET.SubElement(case, "system-out").text = remarks

    tree = ET.ElementTree(suite)
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def table(headers, rows):
    """Render an HTML table with escaped text cells."""
    def cells(tag, values):
        return "".join(
            f"<{tag}>{escape(str(value if value is not None else 'Unavailable'))}</{tag}>"
            for value in values
        )

    head = f"<thead><tr>{cells('th', headers)}</tr></thead>"
    body = "".join(f"<tr>{cells('td', row)}</tr>" for row in rows)
    return f"<table>{head}<tbody>{body}</tbody></table>"


def display_time(timestamp):
    """Convert a recorded UTC timestamp to IST for display."""
    if not timestamp:
        return None

    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.fromisoformat(timestamp).astimezone(ist).strftime(
        "%d-%b-%Y %H:%M:%S IST"
    )


def display_duration(seconds):
    """Format elapsed seconds for display."""
    return None if seconds is None else f"{seconds:.3f} s"


def write_html(report, path):
    """Render the standalone HTML report used as the Jenkins email body."""
    build = report["build"]
    timing = report["run_timing"] or {}
    counts = report["status_counts"]
    tests = report["tests"]

    suite_rows = [
        ("Storage", report["storage_status"], "—", "—", "—", "—", "—", "—", "—"),
        (
            "Network",
            report["run_status"],
            *(counts.get(status, 0) for status in STATUS_LABELS[:6]),
            display_duration(timing.get("duration_seconds")),
        ),
    ]

    layer_rows = []
    for layer in sorted({result["category"] or "Uncategorized" for result in tests}):
        layer_tests = [
            result for result in tests
            if (result["category"] or "Uncategorized") == layer
        ]
        layer_counts = Counter(result["status"] for result in layer_tests)
        durations = [
            result["duration_seconds"] for result in layer_tests
            if result["duration_seconds"] is not None
        ]
        layer_rows.append((
            layer,
            len(layer_tests),
            *(layer_counts.get(status, 0) for status in STATUS_LABELS),
            display_duration(sum(durations) if durations else None),
        ))

    attention = [
        (result["test_case_id"], result["status"], result["remarks"])
        for result in tests if result["status"] != "PASS"
    ]
    if report["run_reason"]:
        attention.insert(0, ("Run", report["run_status"], report["run_reason"]))

    if attention:
        outcome_html = table(("Test case", "Status", "Details"), attention)
    elif tests and counts.get("PASS") == len(tests) and report["run_status"] == "PASS":
        outcome_html = (
            f"<p>All {len(tests)} network tests passed. "
            f"Failed: {counts.get('FAIL', 0)} · "
            f"Blocked: {counts.get('BLOCKED', 0)} · "
            f"Skipped: {counts.get('SKIPPED', 0)}.</p>"
        )
    elif not tests:
        outcome_html = "<p>No network tests ran.</p>"
    else:
        outcome_html = f"<p>Run status: {escape(report['run_status'])}.</p>"

    # Interface names come from the DUT snapshot. Alias mappings are separate.
    interfaces = ", ".join(report.get("detected_interfaces", []))
    if interfaces:
        resource_text = (
            f"Detected DUT network interfaces: {interfaces}. "
            "No EmbITE alias was verified."
        )
    elif report.get("interface_snapshot_available"):
        resource_text = "The DUT reported no network interfaces other than loopback."
    else:
        resource_text = "DUT interface information was unavailable for this run."

    build_url = build["url"]
    parsed_url = urlsplit(build_url) if build_url else None
    if (
        parsed_url
        and parsed_url.scheme in ("http", "https")
        and parsed_url.hostname
        and not parsed_url.username
        and not parsed_url.password
        and not parsed_url.query
        and not parsed_url.fragment
    ):
        base = build_url.rstrip("/") + "/"
        links = [
            ("Jenkins build", base),
            ("HTML report", base + "artifact/reports/summary.html"),
            ("Build artifacts", base + "artifact/"),
        ]
        links_html = "<ul>" + "".join(
            f'<li><a href="{escape(url, quote=True)}">{escape(label)}</a></li>'
            for label, url in links
        ) + "</ul>"
    else:
        links_html = "<p>Jenkins links are unavailable for this run.</p>"

    run_info = [
        ("Project", report["project"]),
        ("Status", report["run_status"]),
        ("Scope", report["scope"]),
        ("Build number", build["number"]),
        ("Jenkins job", build["job"]),
        ("Jenkins node", build["node"]),
        ("Triggered by", build["trigger"]),
        ("Start", display_time(timing.get("started_at"))),
        ("End", display_time(timing.get("finished_at"))),
        ("Duration", display_duration(timing.get("duration_seconds"))),
    ]
    individual_rows = (
        (
            result["test_case_id"],
            result["category"],
            result["description"],
            result["status"],
            display_duration(result["duration_seconds"]),
            result["remarks"],
        )
        for result in tests
    )
    artifact_rows = [(artifact,) for artifact in report["artifacts"]]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>EmbITE Validation Report</title>
<style>
body {{font: 15px Arial, sans-serif; color: #172235; margin: 24px auto; max-width: 1100px; padding: 0 16px;}}
h1, h2 {{color: #263b60;}}
table {{border-collapse: collapse; width: 100%; margin: 0 0 20px;}}
td, th {{border: 1px solid #dce3ed; padding: 8px; text-align: left; vertical-align: top;}}
th {{background: #edf2f8;}}
</style>
</head>
<body>
<h1>EmbITE Automated Validation Report</h1>
<p>Hello Team,</p>
<p>EmbITE recorded the following validation result for {escape(str(report["project"]))}.</p>
{table(("Run information", "Value"), run_info)}
<h2>Target configuration</h2>
{table(("Parameter", "Value"), report["target"].items())}
<h2>Execution summary</h2>
{table(("Suite", "Status", *STATUS_LABELS[:6], "Duration"), suite_rows)}
<h2>Storage validation results</h2>
<p>{escape(report["storage_status"])}</p>
<h2>Network results by layer</h2>
{table(("Layer", "Results", *STATUS_LABELS, "Validator time"), layer_rows)}
<h2>Individual network results</h2>
{table(("Test case", "Layer", "Description", "Status", "Duration", "Details"), individual_rows)}
<h2>Resource mapping</h2>
<p>{escape(resource_text)}</p>
<h2>Failures, blocked tests, and other non-pass outcomes</h2>
{outcome_html}
<h2>Storage safety checks</h2>
<p>Not applicable. This run covered network validation only. No storage tests or storage safety checks were executed.</p>
<h2>Generated reports</h2>
{table(("Artifact",), artifact_rows)}
{links_html}
<h2>Final result</h2>
<p><strong>{escape(report["run_status"])}</strong> — {escape(report["scope"])}</p>
<p>Regards,<br>EmbITE Automation<br>Embedded Intelligent Test Environment<br>NYXSES</p>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def generate_report(
    results, config, run_timing=None, setup_failure=None, *,
    run_status=None, run_reason=None, connected=None, selected_test_id=None,
    target_info=None, network_snapshot=None,
):
    """Write validation artifacts and print the execution summary.

    Empty result lists are supported for blocked setup and zero-test runs.
    Target facts and the network snapshot are optional when SSH is unavailable.
    """
    framework = config["framework"]
    device = config["devices"][config["active_device"]]
    tests = [report_test(result) for result in results]
    counts = dict(Counter(result["status"] for result in tests))

    if setup_failure is not None:
        run_status, run_reason = "BLOCKED", setup_failure
    elif run_status is None:
        run_status = (
            "NO_TESTS" if not tests
            else "PASS" if counts.get("PASS") == len(tests)
            else "FAIL"
        )

    target = {
        "Board": device.get("board"),
        "Target IP": device.get("host"),
        "Username": device.get("username"),
        "Connection method": "SSH",
        "Connection status": (
            "Connected" if connected is True
            else "Connection failed" if connected is False or setup_failure
            else "Unavailable"
        ),
        "Framework version": framework.get("version"),
        "EmbITE version": "Unverified",
        **(target_info or {}),
    }

    report_directory = Path("reports")
    report_directory.mkdir(exist_ok=True)

    network = network_snapshot or {}
    interface_output = network.get("Interfaces") or ""
    interface_names = [
        line.split(maxsplit=1)[0]
        for line in interface_output.splitlines()
        if line.strip()
    ]
    detected_interfaces = [name for name in interface_names if name != "lo"]

    sections = [
        f"{label}\n{value or 'Unavailable'}"
        for label, value in network.items()
    ]
    (report_directory / "network_info.txt").write_text(
        "\n\n".join(sections or ["DUT network snapshot unavailable."]) + "\n",
        encoding="utf-8",
    )

    report = {
        "project": framework["name"],
        "scope": "Network Validation only",
        "selected_test_id": selected_test_id,
        "storage_status": "Not Integrated / Not Executed",
        "run_status": run_status,
        "run_reason": run_reason,
        "setup_failure": run_reason if run_status == "BLOCKED" else None,
        "run_timing": run_timing,
        "build": {
            "number": os.getenv("BUILD_NUMBER"),
            "job": os.getenv("JOB_NAME"),
            "node": os.getenv("NODE_NAME"),
            "url": os.getenv("BUILD_URL"),
            "trigger": os.getenv("EMBITE_BUILD_TRIGGER"),
        },
        "target": target,
        "resource_mappings": {},
        "detected_interfaces": detected_interfaces,
        "interface_snapshot_available": bool(interface_output.strip()),
        "total_tests": len(tests),
        "status_counts": counts,
        "tests": tests,
        "artifacts": [
            "reports/junit.xml",
            "reports/results.json",
            "reports/summary.html",
            "reports/network_info.txt",
        ],
    }

    write_junit(report, report_directory / "junit.xml")
    (report_directory / "results.json").write_text(
        json.dumps(report, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_html(report, report_directory / "summary.html")

    print(f"Run status: {run_status}")
    if run_reason:
        print(run_reason)
    print(f"Total test results: {len(tests)}")
    for status, count in counts.items():
        print(f"{status}: {count}")
    for artifact in report["artifacts"]:
        print(f"Generated: {artifact}")

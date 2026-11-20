"""Run network validation against the configured device under test.

Load the configuration, establish an SSH connection, run the full suite
or a selected test, and generate the validation reports.
"""
"""Run network validation against the configured device under test."""
"""Connect to the DUT, execute network validation, and write run artifacts."""

import sys
from datetime import datetime, timezone
from time import perf_counter

from core.logger import setup_logger
from core.reporter import collect_dut_information, generate_report
from core.ssh import connect_ssh
from core.test_runner import run_tests
from utils.config_loader import load_config


def build_run_timing(started_at, timer):
    """Return UTC timestamps and elapsed seconds for the reporting interval."""
    return {
        "started_at": started_at.isoformat(timespec="milliseconds"),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "duration_seconds": perf_counter() - timer,
    }


def main():
    """Run all cases or the selected case and return the process exit code."""
    started_at = datetime.now(timezone.utc)
    timer = perf_counter()
    config = load_config()
    logger = setup_logger(config)
    selected_test_id = sys.argv[1] if len(sys.argv) > 1 else None

    logger.info("Network validation started.")

    results = []
    target_info = {}
    network_snapshot = {}
    run_status = "BLOCKED"
    run_reason = "SSH connection to the DUT failed."
    ssh = None

    try:
        try:
            ssh = connect_ssh(config, logger)
        except Exception as error:
            logger.error("SSH setup raised %s.", type(error).__name__)

        if ssh is not None:
            try:
                results = run_tests(ssh, config, logger, selected_test_id)
            except Exception as error:
                run_status = "ERROR"
                run_reason = "The framework could not load or execute the test suite."
                logger.error("Suite execution raised %s.", type(error).__name__)
            else:
                if not results:
                    run_status = "NO_TESTS"
                    run_reason = (
                        "The requested test ID matched no configured case."
                        if selected_test_id
                        else "The suite contained no configured cases."
                    )
                elif all(result.get("status") == "PASS" for result in results):
                    run_status = "PASS"
                    run_reason = None
                else:
                    run_status = "FAIL"
                    run_reason = "One or more test cases did not pass."

            # Record suite completion before the separate diagnostic snapshot.
            run_timing = build_run_timing(started_at, timer)
            target_info, network_snapshot = collect_dut_information(ssh)
        else:
            run_timing = build_run_timing(started_at, timer)
            logger.error(run_reason)

        generate_report(
            results,
            config,
            run_timing=run_timing,
            run_status=run_status,
            run_reason=run_reason,
            connected=ssh is not None,
            selected_test_id=selected_test_id,
            target_info=target_info,
            network_snapshot=network_snapshot,
        )
    finally:
        if ssh is not None:
            try:
                ssh.close()
            except Exception as error:
                logger.warning("SSH cleanup raised %s.", type(error).__name__)

    logger.info("Network validation finished with status %s.", run_status)
    return 0 if run_status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())


import sys

from utils.config_loader import load_config
from core.logger import setup_logger
from core.ssh import connect_ssh
from core.test_runner import run_tests
from core.reporter import generate_report


def main():
    config = load_config()
    logger = setup_logger(config)

    selected_test_id = sys.argv[1] if len(sys.argv) > 1 else None

    logger.info("Framework Started Successfully")
    logger.info("Configuration Loaded Successfully")

    if selected_test_id:
        logger.info(f"Selected test case: {selected_test_id}")

    ssh = connect_ssh(config, logger)

    if ssh is None:
        logger.error("Framework stopped because SSH connection failed.")
        return 1

    results = run_tests(
        ssh, config, logger, selected_test_id
    )

    if selected_test_id and not results:
        logger.error(f"No results found for test case: {selected_test_id}")
        ssh.close()
        return 1

    generate_report(results, config)

    ssh.close()

    logger.info("SSH connection closed successfully.")

    failed_tests = [
        result for result in results
        if result.get("status") != "PASS"
    ]

    if failed_tests:
        logger.error(
            f"Framework completed with {len(failed_tests)} "
            "failed or unsupported test cases."
        )
        return 1

    logger.info("All validation test cases passed.")
    print("Framework executed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

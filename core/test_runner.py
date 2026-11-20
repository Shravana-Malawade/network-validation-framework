"""Load and execute network validation cases from the layer YAML files."""

from time import perf_counter

import yaml

from core.test_registry import CONFIG_AWARE_MODULES, TEST_REGISTRY


def load_test_cases():
    """Return all configured test cases in layer and YAML order."""
    test_files = [
        "validation/layer1/test_cases.yaml",
        "validation/layer2/test_cases.yaml",
        "validation/layer3/test_cases.yaml",
        "validation/layer4/test_cases.yaml",
    ]

    test_cases = []
    for test_file in test_files:
        with open(test_file, encoding="utf-8") as file:
            cases = yaml.safe_load(file)
            if cases:
                test_cases.extend(cases)

    return test_cases


def run_tests(ssh, config, logger, selected_test_id=None):
    """Run the selected cases and return their results in execution order.

    An unexpected validator exception ends the run because the DUT state
    may be uncertain. Completed results are retained and remaining cases
    are recorded as blocked.
    """
    logger.info("Test execution started")
    test_cases = load_test_cases()

    if selected_test_id:
        test_cases = [
            case for case in test_cases
            if case.get("test_case_id") == selected_test_id
        ]
        if not test_cases:
            logger.error("Requested test case was not found.")
            return []

    results = []

    for index, test_case in enumerate(test_cases):
        test_id = test_case["test_case_id"]
        module = test_case["module"]
        logger.info("Executing test case: %s", test_id)

        metadata = {
            key: test_case.get(key)
            for key in ("test_case_id", "category", "type", "priority", "description")
        }

        if module not in TEST_REGISTRY:
            results.append({
                **metadata,
                "status": "NOT_SUPPORTED",
                "report_detail": "No validator is registered for this test.",
            })
            continue

        test_function = TEST_REGISTRY[module]
        args = (ssh, test_case, logger)
        if module in CONFIG_AWARE_MODULES:
            args += (config,)

        started_at = perf_counter()
        try:
            result = test_function(*args)
            if not isinstance(result, dict) or not isinstance(result.get("status"), str):
                raise TypeError("Validator returned an invalid result.")
        except Exception as error:
            logger.error(
                "Validator stopped at %s (%s).",
                test_id,
                type(error).__name__,
            )
            results.append({
                **metadata,
                "status": "ERROR",
                "duration_seconds": perf_counter() - started_at,
                "report_detail": "Validator raised an unexpected exception.",
            })

            for remaining in test_cases[index + 1:]:
                results.append({
                    **{
                        key: remaining.get(key)
                        for key in (
                            "test_case_id", "category", "type",
                            "priority", "description",
                        )
                    },
                    "status": "BLOCKED",
                    "report_detail": "Execution stopped after a validator error.",
                })
            break

        results.append({
            **metadata,
            **result,
            "duration_seconds": perf_counter() - started_at,
        })

    logger.info("Test execution completed")
    return results

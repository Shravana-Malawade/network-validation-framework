
import yaml
from core.test_registry import TEST_REGISTRY, CONFIG_AWARE_MODULES


def load_test_cases():
    test_files = [
        "validation/layer1/test_cases.yaml",
        "validation/layer2/test_cases.yaml",
        "validation/layer3/test_cases.yaml",
        "validation/layer4/test_cases.yaml"
    ]

    test_cases = []

    for test_file in test_files:
        with open(test_file, "r") as file:
            cases = yaml.safe_load(file)
            if cases:
                test_cases.extend(cases)

    return test_cases


def run_tests(ssh, config, logger, selected_test_id=None):
    results = []

    logger.info("Test execution started")

    test_cases = load_test_cases()

    # Run only the requested test case when an ID is provided
    if selected_test_id:
        test_cases = [
            case for case in test_cases
            if case.get("test_case_id") == selected_test_id
        ]

        if not test_cases:
            logger.error(f"Test case not found: {selected_test_id}")
            return []

    for test_case in test_cases:
        test_id = test_case["test_case_id"]

        logger.info(f"Executing test case: {test_id}")

        module = test_case["module"]

        if module in TEST_REGISTRY:
            test_function = TEST_REGISTRY[module]

            if module in CONFIG_AWARE_MODULES:
                result = test_function(
                    ssh, test_case, logger, config
                )
            else:
                result = test_function(
                    ssh, test_case, logger
                )

            results.append(result)

        else:
            results.append({
                "test_case_id": test_id,
                "status": "NOT_SUPPORTED",
                "message": f"Module {module} is not implemented"
            })

    logger.info("Test execution completed")

    return results

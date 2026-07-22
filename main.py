"""
Main entry point for the Network Validation Framework.
"""
from utils.config_loader import load_config


def main():
    """
    Start the Network Validation Framework.
    """

    config = load_config()

    print("Framework Name :", config["framework"]["name"])
    print("Version        :", config["framework"]["version"])
    print("Author         :", config["framework"]["author"])
    print("Active Device  :", config["active_device"])


if __name__ == "__main__":
    main()

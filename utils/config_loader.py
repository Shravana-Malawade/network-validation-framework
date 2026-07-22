"""
Configuration Loader Module

This module is responsible for reading the YAML configuration
file and returning the configuration data to the framework.
"""

# Third-party library
import yaml


def load_config():
    """
    Read the YAML configuration file and return the configuration data.

    Returns:
        dict: Configuration loaded from config/config.yaml
    """

    # Path to the configuration file
    config_file = "config/config.yaml"

    # Open the YAML file in read mode
    with open(config_file, "r") as file:

        # Convert YAML into a Python dictionary
        config = yaml.safe_load(file)

    # Return the configuration dictionary
    return config




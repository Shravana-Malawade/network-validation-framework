"""
Test Registry Module

Maintains mapping between test module names
and validation functions.
"""

from validation.layer1.interface import validate_interface


TEST_REGISTRY = {

    "interface": validate_interface

}

"""
Test Registry Module

Maintains mapping between test module names
and validation functions.
"""

from validation.layer1.interface import validate_interface
from validation.layer1.link import validate_link, validate_operstate
from validation.layer1.speed import validate_speed
from validation.layer1.duplex import validate_duplex

from validation.layer2.mac import validate_mac
from validation.layer2.statistics import validate_statistics
from validation.layer2.ethernet import validate_ethernet


TEST_REGISTRY = {

    "interface": validate_interface,

    "link": validate_link,

    "speed": validate_speed,

    "duplex": validate_duplex,

    "operstate": validate_operstate,

    "mac": validate_mac,

    "statistics": validate_statistics,

    "ethernet": validate_ethernet

}

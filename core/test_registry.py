"""
Test Registry Module

Maintains mapping between test module names
and validation functions.
"""

from validation.layer1.interface import validate_interface
from validation.layer2.arp import validate_arp
from validation.layer2.mac import validate_mac
from validation.layer3.ip import validate_ip
from validation.layer4.tcp import validate_tcp


TEST_REGISTRY = {

    "interface": validate_interface,

    "arp": validate_arp,

    "mac": validate_mac,

    "ip": validate_ip,

    "tcp": validate_tcp







}

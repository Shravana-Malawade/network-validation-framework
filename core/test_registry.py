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
from validation.layer2.arp import validate_arp

from validation.layer3.ip import validate_ip
from validation.layer3.dhcp import validate_dhcp
from validation.layer3.gateway import validate_gateway
from validation.layer3.static_ip import validate_static_ip
from validation.layer3.ipv6 import (
    validate_ipv6_global,
    validate_ipv6_link_local
)
from validation.layer3.ping import validate_ping

from validation.layer4.tcp import (
    validate_tcp_connection,
    validate_tcp_payload
)


TEST_REGISTRY = {

    "interface": validate_interface,

    "link": validate_link,

    "speed": validate_speed,

    "duplex": validate_duplex,

    "operstate": validate_operstate,

    "mac": validate_mac,

    "statistics": validate_statistics,

    "ethernet": validate_ethernet,

    "arp": validate_arp,

    "ip": validate_ip,

    "dhcp": validate_dhcp,

    "gateway": validate_gateway,

    "static_ip": validate_static_ip,

    "ipv6_global": validate_ipv6_global,

    "ipv6_link_local": validate_ipv6_link_local,

    "ping": validate_ping,

    "tcp_connection": validate_tcp_connection,

    "tcp_payload": validate_tcp_payload,
}


# These modules require access to the
# complete framework configuration.
CONFIG_AWARE_MODULES = {
    "tcp_payload"
}

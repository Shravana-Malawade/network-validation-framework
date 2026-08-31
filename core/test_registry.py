"""
Test Registry Module

Maintains mapping between test module names
and validation functions.
"""

from validation.layer1.interface import validate_interface
from validation.layer1.link import validate_link

from validation.layer2.arp import validate_arp
from validation.layer2.mac import validate_mac
from validation.layer2.ethernet import validate_ethernet
from validation.layer2.statistics import validate_statistics

from validation.layer3.ip import validate_ip
from validation.layer3.gateway import validate_gateway
from validation.layer3.ping import (
    validate_ping,
    validate_peer_ping
)

from validation.layer4.tcp import (
    validate_tcp,
    validate_tcp_payload,
    validate_tcp_bidirectional
)

from validation.layer4.udp import (
    validate_udp_payload,
    validate_udp_bidirectional
)


from validation.layer4.throughput import (
    validate_tcp_throughput
)

TEST_REGISTRY = {

    "interface": validate_interface,

    "link": validate_link,

    "arp": validate_arp,

    "mac": validate_mac,

    "ethernet": validate_ethernet,

    "statistics": validate_statistics,

    "ip": validate_ip,

    "gateway": validate_gateway,

    "ping": validate_ping,

    "peer_ping": validate_peer_ping,

    "tcp": validate_tcp,

    "tcp_payload": validate_tcp_payload,

    "udp_payload": validate_udp_payload,

    "tcp_bidirectional": validate_tcp_bidirectional,

    "udp_bidirectional": validate_udp_bidirectional,

    "tcp_throughput": validate_tcp_throughput,

}

"""
Layer 4 Throughput Validation Module

Validates bidirectional TCP throughput
between peer DUTs using iperf3.
"""

import json

from core.ssh import connect_device_ssh


def validate_tcp_throughput(
    ssh,
    test_case,
    logger,
    config
):
    """
    Validate bidirectional TCP throughput
    using iperf3.
    """

    logger.info(
        "Starting TCP throughput validation"
    )

    active_device_name = config["active_device"]
    devices = config["devices"]

    active_device = devices[active_device_name]

    peer_device_name = None

    for device_name in devices:
        if device_name != active_device_name:
            peer_device_name = device_name
            break

    if peer_device_name is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Peer DUT is not configured"
        }

    peer_device = devices[peer_device_name]

    active_host = active_device["host"]
    peer_host = peer_device["host"]

    duration = test_case.get(
        "duration",
        10
    )

    minimum_mbps = test_case.get(
        "minimum_throughput_mbps",
        200
    )

    peer_ssh = connect_device_ssh(
        peer_device,
        logger
    )

    if peer_ssh is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
            f"Unable to connect to peer DUT: "
            f"{peer_host}"
        }

    try:

        #
        # Verify iperf3 exists on both DUTs
        #

        stdin, stdout, stderr = ssh.exec_command(
            "command -v iperf3"
        )

        active_iperf = (
            stdout.read().decode().strip()
        )

        if not active_iperf:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                "iperf3 is not installed on active DUT"
            }

        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                "command -v iperf3"
            )
        )

        peer_iperf = (
            stdout.read().decode().strip()
        )

        if not peer_iperf:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                "iperf3 is not installed on peer DUT"
            }

        #
        # Forward throughput
        # Active DUT -> Peer DUT
        #

        logger.info(
            f"TCP throughput forward: "
            f"{active_host} -> {peer_host}"
        )

        peer_ssh.exec_command(
            "pkill -f 'iperf3 -s' || true"
        )

        peer_ssh.exec_command(
            "nohup iperf3 -s -1 "
            ">/tmp/iperf_server.log "
            "2>&1 </dev/null &"
        )

        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )

        stdout.read()

        forward_command = (
            f"iperf3 -c {peer_host} "
            f"-t {duration} -J"
        )

        stdin, stdout, stderr = ssh.exec_command(
            forward_command
        )

        forward_output = (
            stdout.read().decode().strip()
        )

        forward_error = (
            stderr.read().decode().strip()
        )

        forward_status = (
            stdout.channel.recv_exit_status()
        )

        if forward_status != 0:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                f"Forward iperf3 test failed: "
                f"{forward_error}"
            }

        try:
            forward_json = json.loads(
                forward_output
            )

            forward_bps = (
                forward_json["end"]
                ["sum_received"]
                ["bits_per_second"]
            )

            forward_mbps = (
                forward_bps / 1_000_000
            )

        except (
            KeyError,
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                "Unable to parse forward "
                "iperf3 result"
            }

        logger.info(
            f"Forward throughput: "
            f"{forward_mbps:.2f} Mbps"
        )

        #
        # Reverse throughput
        # Peer DUT -> Active DUT
        #

        logger.info(
            f"TCP throughput reverse: "
            f"{peer_host} -> {active_host}"
        )

        peer_ssh.exec_command(
            "pkill -f 'iperf3 -s' || true"
        )

        peer_ssh.exec_command(
            "nohup iperf3 -s -1 "
            ">/tmp/iperf_server.log "
            "2>&1 </dev/null &"
        )

        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )

        stdout.read()

        reverse_command = (
            f"iperf3 -c {peer_host} "
            f"-t {duration} -R -J"
        )

        stdin, stdout, stderr = ssh.exec_command(
            reverse_command
        )

        reverse_output = (
            stdout.read().decode().strip()
        )

        reverse_error = (
            stderr.read().decode().strip()
        )

        reverse_status = (
            stdout.channel.recv_exit_status()
        )

        if reverse_status != 0:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                f"Reverse iperf3 test failed: "
                f"{reverse_error}"
            }

        try:
            reverse_json = json.loads(
                reverse_output
            )

            reverse_bps = (
                reverse_json["end"]
                ["sum_received"]
                ["bits_per_second"]
            )

            reverse_mbps = (
                reverse_bps / 1_000_000
            )

        except (
            KeyError,
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                "Unable to parse reverse "
                "iperf3 result"
            }

        logger.info(
            f"Reverse throughput: "
            f"{reverse_mbps:.2f} Mbps"
        )

        #
        # Threshold validation
        #

        if (
            forward_mbps >= minimum_mbps
            and
            reverse_mbps >= minimum_mbps
        ):
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "PASS",
                "remarks":
                f"TCP throughput verified: "
                f"forward={forward_mbps:.2f} Mbps, "
                f"reverse={reverse_mbps:.2f} Mbps, "
                f"minimum={minimum_mbps} Mbps"
            }

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
            f"TCP throughput below threshold: "
            f"forward={forward_mbps:.2f} Mbps, "
            f"reverse={reverse_mbps:.2f} Mbps, "
            f"minimum={minimum_mbps} Mbps"
        }

    finally:

        peer_ssh.exec_command(
            "pkill -f 'iperf3 -s' || true"
        )

        peer_ssh.close()

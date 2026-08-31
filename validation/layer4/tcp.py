"""
TCP Validation Module

Validates:
1. TCP connection establishment between peer DUTs.
2. TCP payload transfer between peer DUTs.
"""

from core.ssh import connect_device_ssh


def _get_peer_devices(config):
    """
    Return active and peer device information.

    Args:
        config:
            Framework configuration.

    Returns:
        tuple:
            active_device, peer_device
    """

    active_device_name = config["active_device"]
    devices = config["devices"]

    active_device = devices[active_device_name]

    peer_device = None

    for device_name, device in devices.items():
        if device_name != active_device_name:
            peer_device = device
            break

    return active_device, peer_device


def validate_tcp(ssh, test_case, logger, config):
    """
    Validate TCP connection establishment
    from active DUT to peer DUT.
    """

    logger.info(
        "Starting TCP connection validation"
    )

    active_device, peer_device = _get_peer_devices(
        config
    )

    if peer_device is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Peer DUT is not configured"
        }

    active_host = active_device["host"]
    peer_host = peer_device["host"]

    port = test_case.get("port", 22)

    logger.info(
        f"Testing TCP connection: "
        f"{active_host} -> {peer_host}:{port}"
    )

    command = (
        f"timeout 5 bash -c "
        f"'cat < /dev/null > /dev/tcp/"
        f"{peer_host}/{port}'"
    )

    stdin, stdout, stderr = ssh.exec_command(
        command
    )

    stdout.read()

    error = stderr.read().decode().strip()

    exit_status = (
        stdout.channel.recv_exit_status()
    )

    if exit_status == 0:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
            f"TCP connection successful: "
            f"{active_host} -> {peer_host}:{port}"
        }

    return {
        "test_case_id": test_case["test_case_id"],
        "category": test_case["category"],
        "type": test_case["type"],
        "priority": test_case["priority"],
        "description": test_case["description"],
        "status": "FAIL",
        "remarks":
        f"TCP connection failed: "
        f"{active_host} -> {peer_host}:{port}. "
        f"{error}"
    }


def validate_tcp_payload(
    ssh,
    test_case,
    logger,
    config
):
    """
    Validate actual TCP payload transfer
    from active DUT to peer DUT.
    """

    logger.info(
        "Starting TCP payload validation"
    )

    active_device, peer_device = _get_peer_devices(
        config
    )

    if peer_device is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Peer DUT is not configured"
        }

    active_host = active_device["host"]
    peer_host = peer_device["host"]

    port = test_case.get("port", 5001)

    payload = "NETWORK_VALIDATION_TCP_TEST"

    receive_file = (
        "/tmp/tcp_payload_received.txt"
    )

    logger.info(
        f"TCP payload test: "
        f"{active_host} -> {peer_host}:{port}"
    )

    # Connect to peer DUT
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
        # Clean previous test files/processes
        peer_ssh.exec_command(
            f"rm -f {receive_file}"
        )

        peer_ssh.exec_command(
            f"pkill -f 'nc -l {port}' || true"
        )

        # Start TCP listener on peer DUT
        listener_command = (
            f"nohup timeout 10 nc -l {port} "
            f"> {receive_file} "
            f"2>/tmp/tcp_listener_error.log "
            f"</dev/null &"
        )

        peer_ssh.exec_command(
            listener_command
        )

        # Allow listener to start
        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )

        stdout.read()

        # Send known payload from active DUT
        send_command = (
            f"echo '{payload}' | "
            f"nc -N {peer_host} {port}"
        )

        stdin, stdout, stderr = ssh.exec_command(
            send_command
        )

        stdout.read()

        send_error = (
            stderr.read().decode().strip()
        )

        send_status = (
            stdout.channel.recv_exit_status()
        )

        if send_status != 0:
            return {
                "test_case_id":
                test_case["test_case_id"],

                "category":
                test_case["category"],

                "type":
                test_case["type"],

                "priority":
                test_case["priority"],

                "description":
                test_case["description"],

                "status": "FAIL",

                "remarks":
                f"TCP payload send failed: "
                f"{send_error}"
            }

        # Allow peer to write received data
        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                "sleep 1"
            )
        )

        stdout.read()

        # Read received payload
        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                f"cat {receive_file}"
            )
        )

        received_payload = (
            stdout.read()
            .decode()
            .strip()
        )

        logger.info(
            f"Payload sent     : {payload}"
        )

        logger.info(
            f"Payload received : "
            f"{received_payload}"
        )

        if received_payload == payload:
            return {
                "test_case_id":
                test_case["test_case_id"],

                "category":
                test_case["category"],

                "type":
                test_case["type"],

                "priority":
                test_case["priority"],

                "description":
                test_case["description"],

                "status": "PASS",

                "remarks":
                f"TCP payload verified: "
                f"{active_host} -> "
                f"{peer_host}:{port}"
            }

        return {
            "test_case_id":
            test_case["test_case_id"],

            "category":
            test_case["category"],

            "type":
            test_case["type"],

            "priority":
            test_case["priority"],

            "description":
            test_case["description"],

            "status": "FAIL",

            "remarks":
            f"TCP payload mismatch. "
            f"Sent: {payload}, "
            f"Received: {received_payload}"
        }

    finally:
        peer_ssh.exec_command(
            f"rm -f {receive_file}"
        )

        peer_ssh.close()





def validate_tcp_bidirectional(
    ssh,
    test_case,
    logger,
    config
):
    """
    Validate TCP payload transfer in both directions
    between active DUT and peer DUT.
    """

    logger.info(
        "Starting bidirectional TCP payload validation"
    )

    active_device, peer_device = _get_peer_devices(
        config
    )

    if peer_device is None:
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "Peer DUT is not configured"
        }

    active_host = active_device["host"]
    peer_host = peer_device["host"]

    port_forward = test_case.get(
        "forward_port",
        5003
    )

    port_reverse = test_case.get(
        "reverse_port",
        5004
    )

    payload_forward = (
        "NETWORK_VALIDATION_TCP_FORWARD"
    )

    payload_reverse = (
        "NETWORK_VALIDATION_TCP_REVERSE"
    )

    forward_file = (
        "/tmp/tcp_forward_received.txt"
    )

    reverse_file = (
        "/tmp/tcp_reverse_received.txt"
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
        # Active DUT -> Peer DUT
        peer_ssh.exec_command(
            f"rm -f {forward_file}"
        )

        listener_command = (
            f"nohup timeout 10 "
            f"nc -l {port_forward} "
            f"> {forward_file} "
            f"2>/tmp/tcp_forward_error.log "
            f"</dev/null &"
        )

        peer_ssh.exec_command(
            listener_command
        )

        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )
        stdout.read()

        send_command = (
            f"echo '{payload_forward}' | "
            f"nc -N {peer_host} {port_forward}"
        )

        stdin, stdout, stderr = ssh.exec_command(
            send_command
        )

        stdout.read()

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
                "Forward TCP payload send failed"
            }

        stdin, stdout, stderr = peer_ssh.exec_command(
            "sleep 1"
        )
        stdout.read()

        stdin, stdout, stderr = peer_ssh.exec_command(
            f"cat {forward_file}"
        )

        received_forward = (
            stdout.read().decode().strip()
        )

        if received_forward != payload_forward:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                "Forward TCP payload mismatch"
            }

        # Peer DUT -> Active DUT
        ssh.exec_command(
            f"rm -f {reverse_file}"
        )

        reverse_listener = (
            f"nohup timeout 10 "
            f"nc -l {port_reverse} "
            f"> {reverse_file} "
            f"2>/tmp/tcp_reverse_error.log "
            f"</dev/null &"
        )

        ssh.exec_command(
            reverse_listener
        )

        stdin, stdout, stderr = peer_ssh.exec_command(
            "sleep 1"
        )
        stdout.read()

        reverse_send = (
            f"echo '{payload_reverse}' | "
            f"nc -N {active_host} {port_reverse}"
        )

        stdin, stdout, stderr = peer_ssh.exec_command(
            reverse_send
        )

        stdout.read()

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
                "Reverse TCP payload send failed"
            }

        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )
        stdout.read()

        stdin, stdout, stderr = ssh.exec_command(
            f"cat {reverse_file}"
        )

        received_reverse = (
            stdout.read().decode().strip()
        )

        if received_reverse != payload_reverse:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                "Reverse TCP payload mismatch"
            }

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
            f"Bidirectional TCP payload verified: "
            f"{active_host} <-> {peer_host}"
        }

    finally:
        peer_ssh.exec_command(
            f"rm -f {forward_file}"
        )

        ssh.exec_command(
            f"rm -f {reverse_file}"
        )

        peer_ssh.close()

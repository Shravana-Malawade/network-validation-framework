"""
UDP Peer Payload Validation Module

Validates UDP payload transfer
from the active DUT to a configured peer DUT.
"""

from core.ssh import connect_device_ssh


def validate_udp_payload(
    ssh,
    test_case,
    logger,
    config
):
    """
    Validate UDP payload transfer
    from the active DUT to the peer DUT.

    Args:
        ssh:
            Active SSH connection to active DUT.

        test_case:
            Test case dictionary.

        logger:
            Framework logger.

        config:
            Framework configuration.

    Returns:
        dict:
            Validation result.
    """

    logger.info(
        "Starting UDP payload validation"
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

    port = test_case.get("port", 5002)

    payload = "NETWORK_VALIDATION_UDP_TEST"

    receive_file = (
        "/tmp/udp_payload_received.txt"
    )

    logger.info(
        f"UDP payload test: "
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
            f"Unable to connect to peer DUT: {peer_host}"
        }

    try:

        # Remove previous output file
        peer_ssh.exec_command(
            f"rm -f {receive_file}"
        )

        # Kill any old UDP listener
        peer_ssh.exec_command(
            f"pkill -f 'nc -u -l {port}' || true"
        )

        # Start UDP listener on peer DUT
        listener_command = (
            f"nohup timeout 10 nc -u -l {port} "
            f"> {receive_file} "
            f"2>/tmp/udp_listener_error.log "
            f"</dev/null &"
        )

        peer_ssh.exec_command(
            listener_command
        )

        # Wait for listener to start
        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )

        stdout.read()

        # Send UDP payload from active DUT
        send_command = (
            f"echo '{payload}' | "
            f"nc -u -w 2 {peer_host} {port}"
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
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "FAIL",
                "remarks":
                f"UDP payload send failed: "
                f"{send_error}"
            }

        # Wait for receiver to write data
        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                "sleep 1"
            )
        )

        stdout.read()

        # Read received UDP payload
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
            f"UDP payload sent: {payload}"
        )

        logger.info(
            f"UDP payload received: "
            f"{received_payload}"
        )

        if received_payload == payload:
            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "PASS",
                "remarks":
                f"UDP payload verified: "
                f"{active_host} -> "
                f"{peer_host}:{port}"
            }

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
            f"UDP payload mismatch. "
            f"Sent: {payload}, "
            f"Received: {received_payload}"
        }

    finally:

        peer_ssh.exec_command(
            f"pkill -f 'nc -u -l {port}' || true"
        )

        peer_ssh.exec_command(
            f"rm -f {receive_file}"
        )

        peer_ssh.close()


def validate_udp_bidirectional(
    ssh,
    test_case,
    logger,
    config
):
    """
    Validate UDP payload transfer in both directions
    between active DUT and peer DUT.
    """

    logger.info(
        "Starting bidirectional UDP payload validation"
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

    forward_port = test_case.get(
        "forward_port",
        5005
    )

    reverse_port = test_case.get(
        "reverse_port",
        5006
    )

    forward_payload = (
        "NETWORK_VALIDATION_UDP_FORWARD"
    )

    reverse_payload = (
        "NETWORK_VALIDATION_UDP_REVERSE"
    )

    forward_file = (
        "/tmp/udp_forward_received.txt"
    )

    reverse_file = (
        "/tmp/udp_reverse_received.txt"
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
            f"Unable to connect to peer DUT: {peer_host}"
        }

    try:

        #
        # Direction 1:
        # Active DUT -> Peer DUT
        #

        logger.info(
            f"UDP forward test: "
            f"{active_host} -> "
            f"{peer_host}:{forward_port}"
        )

        peer_ssh.exec_command(
            f"rm -f {forward_file}"
        )

        peer_ssh.exec_command(
            f"pkill -f 'nc -u -l {forward_port}' "
            f"|| true"
        )

        forward_listener = (
            f"nohup timeout 10 "
            f"nc -u -l {forward_port} "
            f"> {forward_file} "
            f"2>/tmp/udp_forward_error.log "
            f"</dev/null &"
        )

        peer_ssh.exec_command(
            forward_listener
        )

        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )

        stdout.read()

        forward_send = (
            f"echo '{forward_payload}' | "
            f"nc -u -w 2 "
            f"{peer_host} {forward_port}"
        )

        stdin, stdout, stderr = ssh.exec_command(
            forward_send
        )

        stdout.read()

        forward_status = (
            stdout.channel.recv_exit_status()
        )

        if forward_status != 0:
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
                "Forward UDP payload send failed"
            }

        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                "sleep 1"
            )
        )

        stdout.read()

        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                f"cat {forward_file}"
            )
        )

        received_forward = (
            stdout.read()
            .decode()
            .strip()
        )

        logger.info(
            f"Forward UDP payload sent: "
            f"{forward_payload}"
        )

        logger.info(
            f"Forward UDP payload received: "
            f"{received_forward}"
        )

        if received_forward != forward_payload:
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
                "Forward UDP payload mismatch"
            }

        #
        # Direction 2:
        # Peer DUT -> Active DUT
        #

        logger.info(
            f"UDP reverse test: "
            f"{peer_host} -> "
            f"{active_host}:{reverse_port}"
        )

        ssh.exec_command(
            f"rm -f {reverse_file}"
        )

        ssh.exec_command(
            f"pkill -f 'nc -u -l {reverse_port}' "
            f"|| true"
        )

        reverse_listener = (
            f"nohup timeout 10 "
            f"nc -u -l {reverse_port} "
            f"> {reverse_file} "
            f"2>/tmp/udp_reverse_error.log "
            f"</dev/null &"
        )

        ssh.exec_command(
            reverse_listener
        )

        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                "sleep 1"
            )
        )

        stdout.read()

        reverse_send = (
            f"echo '{reverse_payload}' | "
            f"nc -u -w 2 "
            f"{active_host} {reverse_port}"
        )

        stdin, stdout, stderr = (
            peer_ssh.exec_command(
                reverse_send
            )
        )

        stdout.read()

        reverse_status = (
            stdout.channel.recv_exit_status()
        )

        if reverse_status != 0:
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
                "Reverse UDP payload send failed"
            }

        stdin, stdout, stderr = ssh.exec_command(
            "sleep 1"
        )

        stdout.read()

        stdin, stdout, stderr = ssh.exec_command(
            f"cat {reverse_file}"
        )

        received_reverse = (
            stdout.read()
            .decode()
            .strip()
        )

        logger.info(
            f"Reverse UDP payload sent: "
            f"{reverse_payload}"
        )

        logger.info(
            f"Reverse UDP payload received: "
            f"{received_reverse}"
        )

        if received_reverse != reverse_payload:
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
                "Reverse UDP payload mismatch"
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
            "status": "PASS",
            "remarks":
                f"Bidirectional UDP payload verified: "
                f"{active_host} <-> {peer_host}"
        }

    finally:

        peer_ssh.exec_command(
            f"pkill -f 'nc -u -l {forward_port}' "
            f"|| true"
        )

        ssh.exec_command(
            f"pkill -f 'nc -u -l {reverse_port}' "
            f"|| true"
        )

        peer_ssh.exec_command(
            f"rm -f {forward_file}"
        )

        ssh.exec_command(
            f"rm -f {reverse_file}"
        )

        peer_ssh.close()

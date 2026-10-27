"""
TCP Validation Module

Validates TCP connectivity and TCP payload transfer
between the Device Under Test and peer device.
"""

import socket
import shlex
import time

from core.ssh import connect_device


def validate_tcp_connection(ssh, test_case, logger):
    """
    Validate TCP connection to the DUT.
    """

    logger.info("Starting TCP connection validation")

    transport = ssh.get_transport()

    if transport is None or not transport.is_active():
        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks": "SSH transport is not active"
        }

    # Obtain DUT IP from the active SSH connection
    peer = transport.getpeername()
    dut_host = peer[0]

    # Read TCP port from YAML
    port = test_case.get(
        "target", {}
    ).get(
        "port", 22
    )

    logger.info(f"DUT Host : {dut_host}")
    logger.info(f"TCP Port : {port}")

    try:

        # Create a new independent TCP connection
        tcp_socket = socket.create_connection(
            (dut_host, int(port)),
            timeout=5
        )

        tcp_socket.close()

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "PASS",
            "remarks":
                f"TCP connection successful to "
                f"{dut_host}:{port}"
        }

    except OSError as error:

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
                f"TCP connection failed to "
                f"{dut_host}:{port}: {error}"
        }


def validate_tcp_payload(ssh, test_case, logger, config):
    """
    Validate TCP payload transfer between requester and responder.

    Requester / peer device sends a TCP payload to the DUT.
    The DUT receives the payload and echoes the same payload back.
    The requester verifies that the returned payload matches.
    """

    logger.info("Starting TCP payload validation")

    # Read test parameters from YAML
    target = test_case.get("target", {})

    port = int(
        target.get("port", 5001)
    )

    peer_device = target.get(
        "peer_device",
        "device2"
    )

    payload = target.get(
        "payload",
        "NETWORK_VALIDATION_TCP"
    )

    # Get active DUT
    active_device = config["active_device"]

    dut_host = config["devices"][active_device]["host"]

    peer_host = config["devices"][peer_device]["host"]

    logger.info(
        f"DUT / Responder : {dut_host}"
    )

    logger.info(
        f"Peer / Requester : {peer_host}"
    )

    logger.info(
        f"TCP Port : {port}"
    )

    logger.info(
        f"Payload : {payload}"
    )

    # Connect to peer/requester device
    peer_ssh = connect_device(
        config,
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
                "Unable to establish SSH connection "
                "to peer device"
        }

    try:

        # -------------------------------------------------
        # Start TCP echo server on DUT / responder
        # -------------------------------------------------

        server_code = (
            "import socket;"
            "s=socket.socket();"
            "s.setsockopt(socket.SOL_SOCKET,"
            "socket.SO_REUSEADDR,1);"
            f"s.bind(('0.0.0.0',{port}));"
            "s.listen(1);"
            "s.settimeout(10);"
            "c,a=s.accept();"
            "c.settimeout(5);"
            "d=c.recv(4096);"
            "c.sendall(d);"
            "print(d.decode("
            "'utf-8',errors='replace'),flush=True);"
            "c.close();"
            "s.close()"
        )

        server_command = (
            "python3 -c "
            + shlex.quote(server_code)
        )

        logger.info(
            "Starting TCP server on DUT"
        )

        (
            server_stdin,
            server_stdout,
            server_stderr
        ) = ssh.exec_command(
            server_command
        )

        # Allow time for server to start listening
        time.sleep(1)

        # -------------------------------------------------
        # Run TCP client on peer / requester
        # -------------------------------------------------

        payload_bytes = payload.encode("utf-8")

        client_code = (
            "import socket;"
            f"m={payload_bytes!r};"
            f"s=socket.create_connection("
            f"('{dut_host}',{port}),5);"
            "s.sendall(m);"
            "d=s.recv(4096);"
            "print('SENT='+m.decode(),flush=True);"
            "print('RECEIVED='+d.decode(),flush=True);"
            "print('MATCH='+str(d==m),flush=True);"
            "s.close()"
        )

        client_command = (
            "python3 -c "
            + shlex.quote(client_code)
        )

        logger.info(
            "Sending TCP payload from peer to DUT"
        )

        (
            client_stdin,
            client_stdout,
            client_stderr
        ) = peer_ssh.exec_command(
            client_command
        )

        # Wait for client execution to complete
        client_status = (
            client_stdout.channel.recv_exit_status()
        )

        client_output = (
            client_stdout
            .read()
            .decode()
            .strip()
        )

        client_error = (
            client_stderr
            .read()
            .decode()
            .strip()
        )

        # Wait for server execution to complete
        server_status = (
            server_stdout.channel.recv_exit_status()
        )

        server_output = (
            server_stdout
            .read()
            .decode()
            .strip()
        )

        server_error = (
            server_stderr
            .read()
            .decode()
            .strip()
        )

        logger.info(
            f"TCP client output: {client_output}"
        )

        logger.info(
            f"TCP server output: {server_output}"
        )

        # -------------------------------------------------
        # Validate TCP payload
        # -------------------------------------------------

        if (
            client_status == 0
            and server_status == 0
            and "MATCH=True" in client_output
            and payload in server_output
        ):

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

                "status":
                    "PASS",

                "remarks":
                    f"TCP payload transfer successful: "
                    f"{peer_host} -> "
                    f"{dut_host}:{port}; "
                    f"payload echoed correctly"
            }

        # -------------------------------------------------
        # Failure handling
        # -------------------------------------------------

        error_message = (
            client_error
            or server_error
            or client_output
            or server_output
            or "Payload did not match"
        )

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

            "status":
                "FAIL",

            "remarks":
                f"TCP payload validation failed: "
                f"{error_message}"
        }

    except Exception as error:

        logger.error(
            f"TCP payload validation error: {error}"
        )

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

            "status":
                "FAIL",

            "remarks":
                f"TCP payload validation failed: "
                f"{error}"
        }

    finally:

        peer_ssh.close()

        logger.info(
            "Peer SSH connection closed"
        )

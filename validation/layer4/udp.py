"""
UDP Validation Module

Validates UDP payload transfer between
the requester and responder devices.
"""

import shlex
import time

from core.ssh import connect_device


def validate_udp_payload(ssh, test_case, logger, config):
    """
    Validate UDP payload transfer between requester and responder.

    The peer/requester sends a UDP payload to the DUT/responder.
    The DUT echoes the same payload back.
    """

    logger.info("Starting UDP payload validation")

    target = test_case.get("target", {})

    port = int(
        target.get("port", 5002)
    )

    peer_device = target.get(
        "peer_device",
        "device2"
    )

    payload = target.get(
        "payload",
        "NETWORK_VALIDATION_UDP"
    )

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
        f"UDP Port : {port}"
    )

    logger.info(
        f"Payload : {payload}"
    )

    # Connect to requester / peer
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

        # ---------------------------------------------
        # Start UDP echo server on DUT / responder
        # ---------------------------------------------

        server_code = (
            "import socket;"
            "s=socket.socket("
            "socket.AF_INET,"
            "socket.SOCK_DGRAM);"
            f"s.bind(('0.0.0.0',{port}));"
            "s.settimeout(10);"
            "d,a=s.recvfrom(4096);"
            "print(d.decode("
            "'utf-8',errors='replace'),flush=True);"
            "s.sendto(d,a);"
            "s.close()"
        )

        server_command = (
            "python3 -c "
            + shlex.quote(server_code)
        )

        logger.info(
            "Starting UDP server on DUT"
        )

        (
            server_stdin,
            server_stdout,
            server_stderr
        ) = ssh.exec_command(
            server_command
        )

        # Give the UDP server time to bind
        time.sleep(1)

        # ---------------------------------------------
        # Run UDP client on requester / peer
        # ---------------------------------------------

        payload_bytes = payload.encode("utf-8")

        client_code = (
            "import socket;"
            f"m={payload_bytes!r};"
            "s=socket.socket("
            "socket.AF_INET,"
            "socket.SOCK_DGRAM);"
            "s.settimeout(5);"
            f"s.sendto(m,('{dut_host}',{port}));"
            "d,a=s.recvfrom(4096);"
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
            "Sending UDP payload from peer to DUT"
        )

        (
            client_stdin,
            client_stdout,
            client_stderr
        ) = peer_ssh.exec_command(
            client_command
        )

        client_status = (
            client_stdout.channel.recv_exit_status()
        )

        client_output = (
            client_stdout.read().decode().strip()
        )

        client_error = (
            client_stderr.read().decode().strip()
        )

        server_status = (
            server_stdout.channel.recv_exit_status()
        )

        server_output = (
            server_stdout.read().decode().strip()
        )

        server_error = (
            server_stderr.read().decode().strip()
        )

        logger.info(
            f"UDP client output: {client_output}"
        )

        logger.info(
            f"UDP server output: {server_output}"
        )

        # ---------------------------------------------
        # Validate payload
        # ---------------------------------------------

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
                    f"UDP payload transfer successful: "
                    f"{peer_host} -> "
                    f"{dut_host}:{port}; "
                    f"payload echoed correctly"
            }

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
                f"UDP payload validation failed: "
                f"{error_message}"
        }

    except Exception as error:

        logger.error(
            f"UDP payload validation error: {error}"
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
                f"UDP payload validation failed: "
                f"{error}"
        }

    finally:

        peer_ssh.close()

        logger.info(
            "Peer SSH connection closed"
        )

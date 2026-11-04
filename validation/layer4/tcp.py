
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

    peer = transport.getpeername()
    dut_host = peer[0]

    port = test_case.get(
        "target", {}
    ).get(
        "port", 22
    )

    logger.info(f"DUT Host : {dut_host}")
    logger.info(f"TCP Port : {port}")

    try:

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

    Peer device sends a TCP payload to the DUT.
    DUT receives the payload and echoes it back.
    Peer verifies that the returned payload matches.
    """

    logger.info("Starting TCP payload validation")

    target = test_case.get("target", {})

    port = int(target.get("port", 5001))

    peer_device = target.get(
        "peer_device",
        "device2"
    )

    payload = target.get(
        "payload",
        "NETWORK_VALIDATION_TCP"
    )

    active_device = config["active_device"]

    dut_host = config["devices"][active_device]["host"]

    peer_host = config["devices"][peer_device]["host"]

    logger.info(f"DUT / Responder : {dut_host}")
    logger.info(f"Peer / Requester : {peer_host}")
    logger.info(f"TCP Port : {port}")
    logger.info(f"Payload : {payload}")

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

        # Start TCP echo server on DUT.

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

        logger.info("Starting TCP server on DUT")

        (
            server_stdin,
            server_stdout,
            server_stderr
        ) = ssh.exec_command(server_command)

        time.sleep(1)

        # Run TCP client on peer device.

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
        ) = peer_ssh.exec_command(client_command)

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

        logger.info(f"TCP client output: {client_output}")
        logger.info(f"TCP server output: {server_output}")

        if (
            client_status == 0
            and server_status == 0
            and "MATCH=True" in client_output
            and payload in server_output
        ):

            return {
                "test_case_id": test_case["test_case_id"],
                "category": test_case["category"],
                "type": test_case["type"],
                "priority": test_case["priority"],
                "description": test_case["description"],
                "status": "PASS",
                "remarks":
                    f"TCP payload transfer successful: "
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
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
                f"TCP payload validation failed: "
                f"{error_message}"
        }

    except Exception as error:

        logger.error(
            f"TCP payload validation error: {error}"
        )

        return {
            "test_case_id": test_case["test_case_id"],
            "category": test_case["category"],
            "type": test_case["type"],
            "priority": test_case["priority"],
            "description": test_case["description"],
            "status": "FAIL",
            "remarks":
                f"TCP payload validation failed: {error}"
        }

    finally:

        peer_ssh.close()

        logger.info("Peer SSH connection closed")


def validate_tcp_bidirectional(ssh, test_case, logger, config):
    """
    Validate bidirectional TCP communication.

    Peer sends its own payload to DUT.
    DUT sends a different payload back to peer.
    Both devices verify the received payload.
    """

    logger.info(
        "Starting bidirectional TCP validation"
    )

    peer_ssh = None

    # Build a result using the framework's existing format.
    def make_result(status, remarks):

        return {
            "test_case_id": test_case.get(
                "test_case_id",
                test_case.get("id")
            ),
            "category": test_case.get(
                "category",
                test_case.get("layer", "L4")
            ),
            "type": test_case.get("type"),
            "priority": test_case.get("priority"),
            "description": test_case.get("description"),
            "status": status,
            "remarks": remarks
        }

    try:

        # Read test configuration.

        target = test_case.get("target", {})
        parameters = test_case.get("parameters", {})

        port = int(target["port"])
        peer_device = target["peer_device"]

        dut_payload = str(
            parameters["dut_payload"]
        ).encode("utf-8")

        peer_payload = str(
            parameters["peer_payload"]
        ).encode("utf-8")

        active_device = config["active_device"]

        dut_host = config["devices"][active_device]["host"]

        peer_host = config["devices"][peer_device]["host"]

        logger.info(f"DUT Host : {dut_host}")
        logger.info(f"Peer Host : {peer_host}")
        logger.info(f"TCP Port : {port}")

        logger.info(
            f"DUT Payload : {dut_payload.decode()}"
        )

        logger.info(
            f"Peer Payload : {peer_payload.decode()}"
        )

        # Connect to peer device.

        peer_ssh = connect_device(
            config,
            peer_device,
            logger
        )

        if peer_ssh is None:

            return make_result(
                "FAIL",
                "Unable to establish SSH connection "
                "to peer device"
            )

        # -------------------------------------------------
        # Start TCP server on DUT.
        # -------------------------------------------------

        server_script = f"""
import socket

HOST = "0.0.0.0"
PORT = {port}

DUT_PAYLOAD = {dut_payload!r}
EXPECTED_PEER_PAYLOAD = {peer_payload!r}


def receive_line(conn):

    data = b""

    while bytes([10]) not in data:

        chunk = conn.recv(4096)

        if not chunk:
            break

        data += chunk

    return data.split(bytes([10]), 1)[0]


try:

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.settimeout(15)

        server.bind((HOST, PORT))

        server.listen(1)

        print("SERVER_READY", flush=True)

        conn, address = server.accept()

        with conn:

            conn.settimeout(15)

            received = receive_line(conn)

            receive_match = (
                received == EXPECTED_PEER_PAYLOAD
            )

            conn.sendall(
                DUT_PAYLOAD + bytes([10])
            )

            print(
                "RECEIVED:",
                received.decode(),
                flush=True
            )

            print(
                "SENT:",
                DUT_PAYLOAD.decode(),
                flush=True
            )

            print(
                "RECEIVE_MATCH:",
                receive_match,
                flush=True
            )

            if not receive_match:

                raise ValueError(
                    "Peer payload did not match"
                )

except Exception as error:

    print(
        "SERVER_ERROR:",
        str(error),
        flush=True
    )

    raise
"""

        server_command = (
            "python3 -u -c "
            + shlex.quote(server_script)
        )

        logger.info(
            "Starting bidirectional TCP server on DUT"
        )

        (
            server_stdin,
            server_stdout,
            server_stderr
        ) = ssh.exec_command(server_command)

        # Allow server startup.

        time.sleep(2)

        # -------------------------------------------------
        # Run TCP client on peer device.
        # -------------------------------------------------

        client_script = f"""
import socket

DUT_HOST = {dut_host!r}
PORT = {port}

PEER_PAYLOAD = {peer_payload!r}
EXPECTED_DUT_PAYLOAD = {dut_payload!r}


def receive_line(sock):

    data = b""

    while bytes([10]) not in data:

        chunk = sock.recv(4096)

        if not chunk:
            break

        data += chunk

    return data.split(bytes([10]), 1)[0]


try:

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as client:

        client.settimeout(15)

        client.connect((DUT_HOST, PORT))

        client.sendall(
            PEER_PAYLOAD + bytes([10])
        )

        received = receive_line(client)

        receive_match = (
            received == EXPECTED_DUT_PAYLOAD
        )

        print(
            "SENT:",
            PEER_PAYLOAD.decode()
        )

        print(
            "RECEIVED:",
            received.decode()
        )

        print(
            "RECEIVE_MATCH:",
            receive_match
        )

        if not receive_match:

            raise ValueError(
                "DUT payload did not match"
            )

except Exception as error:

    print(
        "CLIENT_ERROR:",
        str(error)
    )

    raise
"""

        client_command = (
            "python3 -u -c "
            + shlex.quote(client_script)
        )

        logger.info(
            "Sending peer payload to DUT and "
            "receiving DUT payload"
        )

        (
            client_stdin,
            client_stdout,
            client_stderr
        ) = peer_ssh.exec_command(client_command)

        # Collect client output.

        client_output = (
            client_stdout.read().decode(
                errors="replace"
            )
        )

        client_error = (
            client_stderr.read().decode(
                errors="replace"
            )
        )

        client_status = (
            client_stdout.channel.recv_exit_status()
        )

        # Collect server output.

        server_output = (
            server_stdout.read().decode(
                errors="replace"
            )
        )

        server_error = (
            server_stderr.read().decode(
                errors="replace"
            )
        )

        server_status = (
            server_stdout.channel.recv_exit_status()
        )

        logger.info(
            f"TCP client output:\n{client_output}"
        )

        logger.info(
            f"TCP server output:\n{server_output}"
        )

        if client_error:
            logger.error(client_error)

        if server_error:
            logger.error(server_error)

        # -------------------------------------------------
        # Validate both communication directions.
        # -------------------------------------------------

        if (
            client_status == 0
            and server_status == 0
            and "RECEIVE_MATCH: True" in client_output
            and "RECEIVE_MATCH: True" in server_output
        ):

            remark = (
                f"Bidirectional TCP communication successful: "
                f"{peer_host} <-> {dut_host}:{port}; "
                f"both payloads received and matched."
            )

            logger.info(remark)

            return make_result(
                "PASS",
                remark
            )

        remark = (
            "Bidirectional TCP validation failed. "
            f"Client status: {client_status}; "
            f"Server status: {server_status}; "
            f"Client output: {client_output}; "
            f"Server output: {server_output}; "
            f"Client error: {client_error}; "
            f"Server error: {server_error}"
        )

        logger.error(remark)

        return make_result(
            "FAIL",
            remark
        )

    except Exception as error:

        remark = (
            f"Bidirectional TCP validation error: {error}"
        )

        logger.error(remark)

        return make_result(
            "FAIL",
            remark
        )

    finally:

        if peer_ssh is not None:

            peer_ssh.close()

            logger.info(
                "Peer SSH connection closed"
            )

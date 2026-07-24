"""
Command Execution Module

This module is responsible for executing Linux commands
on the Device Under Test (DUT) through an SSH connection.
"""


def execute_command(ssh, command, logger):
    """
    Execute a Linux command on the Device Under Test (DUT).

    Args:
        ssh (paramiko.SSHClient): Connected SSH client object.
        command (str): Linux command to execute.
        logger (logging.Logger): Logger object used for logging.

    Returns:
        str: Command output if execution is successful.
        None: If command execution fails.
    """

    try:

        # Log the command that is going to be executed
        logger.info(f"Executing command: {command}")

        # Execute command on remote DUT using SSH
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read command output
        output = stdout.read().decode().strip()

        # Read command error output
        error = stderr.read().decode().strip()

        # Check whether command execution produced an error
        if error:
            logger.error(
                f"Command execution failed for '{command}': {error}"
            )

            return None

        # Command executed successfully
        logger.info(
            f"Command executed successfully: {command}"
        )

        return output

    except Exception as error:

        logger.error(
            f"Failed to execute command '{command}': {error}"
        )

        return None

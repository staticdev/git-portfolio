"""Command checker use case."""
import subprocess  # nosec


class CommandChecker:
    """Command checker."""

    def check(self, command: str) -> str:
        """Check installation of required commands.

        Args:
            command: checked command.

        Returns:
            str: output message.
        """
        try:
            popen = subprocess.Popen(  # nosec
                command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
            )
            popen.communicate()
        except FileNotFoundError:
            return (
                f"This command requires {command} executable installed and on "
                "system path."
            )
        return ""

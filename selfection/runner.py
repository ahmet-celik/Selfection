import shlex
import subprocess


def run_process(commandline):
    """Executes command in new shell and returns output.

    Args:
        commandline: Command and arguments as a string.

    Returns:
        Line from output of command. You should call like that:

        for line in run_process(commandline):
            print line

    Raises:
        None
    """
    args = shlex.split(commandline)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return stdout.splitlines()
    else:
        raise RuntimeError("Process did not terminate properly!")

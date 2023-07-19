"""Messages for the command-line interface"""
import enum
import sys

__all__ = ('p_header', 'p_pass', 'p_fail', 'p_bold', 'p_warn')


class Colors(enum.StrEnum):
    """ASCII terminal colors"""
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    MAGENTA = "\033[1;35m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"


def p_header(msg: str, end: str = '\n'):
    """Print a heading"""
    msg = msg.strip() + ' '

    sys.stdout.write(f'{Colors.MAGENTA}{msg:=<{term_width - 1}}{Colors.RESET}'
                     f'{end}')


def p_pass(msg: str, end: str = '\n'):
    """Print a message for a passed test"""
    sys.stdout.write(f'  {Colors.GREEN}✔ {msg.strip()}{Colors.RESET}{end}')


def p_fail(msg: str, end: str = '\n', exit_on_fail: t.Optional = None):
    """Print a message for a failed test"""
    if exit_on_fail is None:
        global exit_on_fail_default
        exit_on_fail = exit_on_fail_default

    sys.stderr.write(f'  {Colors.RED}✖ {msg.strip()}{Colors.RESET}{end}')

    if exit_on_fail:
        exit(1)


def p_bold(msg: str, end: str = '\n'):
    """Print a message in bold"""
    sys.stdout.write(f'  {Colors.BOLD}  {msg.strip()}{Colors.RESET}{end}')


def p_warn(msg: str, end: str = '\n'):
    """Print a message for a warning"""
    sys.stderr.write(f'  {Colors.YELLOW}! {msg.strip()}{Colors.RESET}{end}')
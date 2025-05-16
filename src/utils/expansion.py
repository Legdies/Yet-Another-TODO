import os
import sys
from utils.exceptions import DisplayError


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def general_check() -> tuple[bool,str]:
    try:
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            if not os.environ.get('DISPLAY'):
                raise DisplayError

        try:
            import PyQt5
            return True, "PyQt5 is available and GUI display is detected"
        except ImportError:
            raise ImportError("PyQt5 not installed")

    except Exception as e:
        return False, str(e)


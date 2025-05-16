import os
import sys
from utils.exceptions import DisplayError
import logging

logger = logging.getLogger(__name__)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def general_check() -> tuple[bool,str]:
    try:
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            if not os.environ.get('DISPLAY'):
                logger.error(DisplayError)
                raise
        try:
            import PyQt5
            return True, "PyQt5 is available and GUI display is detected"
        except ImportError:
            logger.error(ImportError("Error: PyQt5 is not available"))
            raise
    except Exception as e:
        return False, str(e)


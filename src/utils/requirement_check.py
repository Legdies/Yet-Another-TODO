import sys
import os

def general_check() -> tuple[bool,str]:
    try:
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            if not os.environ.get('DISPLAY'):
                raise
        try:
            import PyQt5
            return True, "PyQt5 is available and GUI display is detected"
        except ImportError:
            raise
    except Exception as e:
        return False, str(e)
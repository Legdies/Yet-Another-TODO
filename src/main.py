import logging
import os
import readchar
from utils import clear, FileManager, general_check

logger = logging.getLogger(__name__)


class MainCLI(FileManager):
    def __init__(self):
        super().__init__()
        clear()
        statement, ErrorCode = general_check()

        if statement:
            print("All requirements meet, launching GUI")
        else:
            print(f"Can't run QT: {ErrorCode}")
            input("Press Enter to continue in CLI...")

    def init_shell(self) -> None:
        try:
            #OS check
            if not os.name == "nt":
                self.fm.path = os.path.expanduser("~/TODO")
                return None

            #Is the dir exist?
            if not os.path.exists(self.fm.path):
                os.mkdir(self.fm.path)
                return None
            return None
        except Exception as e:
            logger.error(e)
            raise

    def basic_shell_input(self):
        self.init_shell()
        clear()
        is_exit_pressed = False
        while not is_exit_pressed:
            print(f"Todo toolkit by LeDIeS V0.1 \n\n\n"
                  f"Options that's available:\n")
            for idx, option in enumerate(self.buttonsMain):
                print(f"{idx}. {option}")
            key = readchar.readkey()
            if key in "012":
                selected = int(key)
                if selected == 2:
                    print("Bye.")
                    input("Press Enter to continue...")
                    is_exit_pressed = True
                if selected == 1:
                    self.create_file()
                if selected == 0:
                    self.edit_file()
        pass


MainCLI().basic_shell_input()

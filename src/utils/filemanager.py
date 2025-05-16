from utils.models import FileManagerModel
from utils.expansion import clear
import logging
import os
import io
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileManager(FileManagerModel):
    def __init__(self):
        super().__init__()

    fm = FileManagerModel()


    sub_menu = ["list tasks",
                "Edit task",
                "Exit"]
    buttonsMain = ["Open File",
                   "Create File",
                   "Exit"]

    def edit_file(self, path = fm.path, filename = fm.filename):
        logger.info("Editing File on")
        print(f"Edit Mode WIP: returning standard path {self.path}")
        for idx, i in enumerate(FileManager().sub_menu):
            print(f"{idx}: {i}")
        input("Press Enter to continue...")
        clear()

    def create_file(self):
        print(f"Creating file: {self.filename} in path: {self.path}")
        os.makedirs(self.path, exist_ok=True)
        with io.open(os.path.join(self.path, self.filename), "w+") as fd:
            print(os.path.join(self.path, self.filename))
            fd.write("")
            fd.close()
        input("Press Enter to continue...")
        clear()

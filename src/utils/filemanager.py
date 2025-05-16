from utils.models import FileManagerModel
from utils.expansion import clear
import os

class FileManager(FileManagerModel):
    fm = FileManagerModel()

    sub_menu = ["list tasks","Edit task", "Exit"]
    buttonsMain = ["Open File", "Create File", "Exit"]

    def edit_file(self):
        print(f"Edit Mode WIP: returning standart path {self.path}")
        input("Press Enter to continue...")
        clear()

    def create_file(self):
        print(f"Creating file: {self.filename} in path: {self.path}")
        input("Press Enter to continue...")
        clear()

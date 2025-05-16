class DisplayError(Exception):
    def __init__(self):
        super().__init__("DISPLAY VARIABLE WAS NOT FOUND OR IT CANT BE USED")

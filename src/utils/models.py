from pydantic import BaseModel
import datetime
from datetime import date
import os
class FileManagerModel(BaseModel):
    path: str = os.path.expanduser('~\TODO')
    filename: str = "list.json"
    date: str = datetime.datetime.now().strftime("%Y%m%d")

class TaskModel(BaseModel):
    name: str
    property: dict
    dateBy: date
    done: bool = False


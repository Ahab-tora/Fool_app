import sqlite3
import json
import data
from data import global_variables
from PySide6.QtWidgets import QMessageBox
def update_recently_opened(path):
    print('updating')
    try:

        with open(global_variables.fool_path + '\\data\\files_data.json', "r") as file:
            data = json.load(file)

        data['recent'].insert(0,path)
        data['recent'] = data['recent'][:10]

        with open(global_variables.fool_path + '\\data\\files_data.json', "w") as file:
            json.dump(data, file, indent=4)


    except Exception as e:
        QMessageBox.warning(None, "Error", f"Could not add file to recent files : {e}")


def set_as_favorite(path):
    try:
        with open(global_variables.fool_path + '\\data\\files_data.json', "r") as file:
            data = json.load(file)

        data['favorites'].insert(0,path)

        with open(global_variables.fool_path + '\\data\\files_data.json', "w") as file:
            json.dump(data, file, indent=4)


    except Exception as e:
        QMessageBox.warning(None, "Error", f"Could not add file to favorite files : {e}")


def connect_and_close_DB(func):
    def connect_and_close_DB_wrapper(table_path:str,*args, **kwargs):
        connection = sqlite3.connect(table_path)
        cursor=connection.cursor()
        func(cursor,table_path,*args, **kwargs)
        connection.close()
        return 
    return connect_and_close_DB_wrapper
        

from typing import Callable
import sqlite3

def connect_and_close(func: Callable) -> Callable:
    def connect_and_close_wrapper(table_path: str, *args, **kwargs):
        connection = sqlite3.connect(table_path)
        cursor = connection.cursor()
        try:
            # Pass the cursor (and connection if needed) to the function
            result = func(cursor, *args, **kwargs)
            connection.commit()  # Commit changes if there are any
        finally:
            connection.close()  # Ensure the connection is always closed
        return result
    return connect_and_close_wrapper




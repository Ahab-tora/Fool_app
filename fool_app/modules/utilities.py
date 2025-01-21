import sqlite3

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



def set_favorite():
    pass
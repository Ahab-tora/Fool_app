import sqlite3
import json
import data
from data import global_variables
from PySide6.QtWidgets import QMessageBox,QWidget,QHBoxLayout,QGroupBox,QGridLayout,QButtonGroup,QPushButton

fool_path = global_variables.fool_path


class Buttons_gridLayout(QWidget):
    def __init__(self,
                 mutually_exclusive:bool = True,
                 buttonsPerRow:int = 5,
                 borderVis:bool = True,
                 boxName:str = 'Placeholder',
                 checkable:bool = True,
                 buttons:list = None,
                 doubleClickConnect:list = None,
                 clickConnect:list = None,
                 ):
        
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.box = QGroupBox(boxName)
        self.boxLayout = QGridLayout()
        self.box.setLayout(self.boxLayout)
        layout.addWidget(self.box)

        self.buttonsGroup = QButtonGroup(self)
        self.buttonsGroup.setExclusive(mutually_exclusive)

        self.buttonsDict = {}
        loop_counter = 0
        grid_row = 0
        for button in buttons:
            if loop_counter % buttonsPerRow == 0:
                grid_row += 1
                loop_counter = 0
            self.buttonsDict[button] = QPushButton(button)
            self.buttonsDict[button].setCheckable(checkable)
            self.buttonsDict[button].setStyleSheet("QPushButton:checked { background-color: #5288B2; }")
            self.buttonsGroup.addButton(self.buttonsDict[button])                 
            self.boxLayout.addWidget(self.buttonsDict[button],grid_row,loop_counter)
            loop_counter += 1

            if checkable:
                self.currentButton = None
                self.buttonsGroup.buttonClicked.connect(self.setCurrentButton)

            if doubleClickConnect:
                for connection in doubleClickConnect:
                    self.buttonsGroup.buttonClicked.connect(connection)
            if clickConnect:
                for connection in clickConnect:
                    self.buttonsGroup.buttonClicked.connect(connection)

    def setCurrentButton(self):
        self.currentButton = self.buttonsGroup.checkedButton()

    def currentButton(self):
        return self.currentButton
    
    def currentButtonName(self):
        if self.currentButton:
            return self.currentButton.text()
        return None

def update_recently_opened(path):
    print('updating')
    try:

        with open(fool_path + '\\data\\files_data.json', "r") as file:
            data = json.load(file)

        data['recent'].insert(0,path)
        data['recent'] = data['recent'][:10]

        with open(fool_path + '\\data\\files_data.json', "w") as file:
            json.dump(data, file, indent=4)


    except Exception as e:
        QMessageBox.warning(None, "Error", f"Could not add file to recent files : {e}")


def set_as_favorite(path):
    try:
        with open(fool_path + '\\data\\files_data.json', "r") as file:
            data = json.load(file)

        data['favorites'].insert(0,path)

        with open(fool_path + '\\data\\files_data.json', "w") as file:
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




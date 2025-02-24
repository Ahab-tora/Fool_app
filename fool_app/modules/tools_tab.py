
#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QButtonGroup,QRadioButton,QAbstractItemView,QHBoxLayout,QListView,QWidget,QLineEdit,QVBoxLayout,QPushButton,QTabWidget,QGroupBox,QDialogButtonBox,QDialog,QLabel,QTableView,QHeaderView
from PySide6.QtWidgets import  QGridLayout, QWidget, QVBoxLayout,QPushButton,QLineEdit, QMessageBox,QSizePolicy
from PySide6.QtGui import QStandardItemModel,QStandardItem,QDrag
from PySide6.QtCore import Qt,QMimeData,QUrl

#--- Standard library imports
import os,shutil,sqlite3,logging,uuid
from pathlib import Path
import requests

#--- data imports

import data
from data import global_variables

#--- --- --- ---#

#types are character,item,prop or set


class Tools_tab(QWidget):
    def __init__(self):
        super().__init__()

        self.loaded = False

        self.tools_tab_layout = QVBoxLayout()
        self.setLayout(self.tools_tab_layout)

        #--- Buttons ---
        self.buttons_group = QGroupBox()
        self.tools_tab_layout.addWidget(self.buttons_group)
        self.buttons_layout = QHBoxLayout()
        self.buttons_group.setLayout(self.buttons_layout)

        self.refresh_tools_button = QPushButton('Refresh tools')
        self.refresh_tools_button.clicked.connect(self.refresh_tools)
        self.buttons_layout.addWidget(self.refresh_tools_button)

        self.open_my_tools_button = QPushButton("Open my tools folder")
        self.open_my_tools_button.clicked.connect(self.open_my_tools)
        self.buttons_layout.addWidget(self.open_my_tools_button)


        self.open_team_tools_button = QPushButton("Open team tools folder")
        self.open_team_tools_button.clicked.connect(self.open_team_tools)
        self.buttons_layout.addWidget(self.open_team_tools_button)

        # --- My tools ---
        self.my_tools_group = QGroupBox("My tools")
        self.tools_tab_layout.addWidget(self.my_tools_group)
        self.my_tools_layout = QGridLayout()
        self.my_tools_group.setLayout(self.my_tools_layout)

        # --- Team tools---
        self.team_tools_group = QGroupBox('Team tools')
        self.tools_tab_layout.addWidget(self.team_tools_group)
        self.team_tools_layout = QGridLayout()
        self.team_tools_group.setLayout(self.team_tools_layout)

        self.refresh_tools()

    def on_display(self):
        self.refresh_tools()

    def refresh_tools(self):
        print('refreshing tools')
        def set_my_tools():

            for x in range(self.team_tools_layout.count()):  
                item = self.team_tools_layout.takeAt(0)  
                if item.widget():  
                    item.widget().deleteLater()

            scripts = []
            scenes = []

            for element in os.listdir(global_variables.fool_path +'\\tools'):
                
                if element.endswith('.py') or element.endswith('.mel'):
                    scripts.append(global_variables.fool_path +'\\tools\\'+element)
                if element.endswith('.ma') or element.endswith('.mb'):
                    scenes.append(global_variables.fool_path +'\\tools\\'+element)

            i = 0
            script_buttons_instances = {}
            for script in scripts:
                script_buttons_instances[script] = Drop_script_button(text=script.split('\\')[-1],parent=self,file=script)

                row = i // 5  
                column = i % 5   

                self.my_tools_layout.addWidget(script_buttons_instances[script], row, column)  
                i+=1
            
            scenes_buttons_instances = {}
            for scene in scenes:
                scenes_buttons_instances[scenes] = Drop_reference_button(text=scene.split('\\')[-1],parent=self,file=scene)

                row = i // 5  
                column = i % 5   

                self.my_tools_layout.addWidget(scenes_buttons_instances[scene], row, column)  
                i+=1
        
        def set_team_tools():
            
            while self.team_tools_layout.count():  
                item = self.team_tools_layout.takeAt(0)  
                if item.widget():  
                    item.widget().deleteLater()

            if not os.path.exists(global_variables.pipeline_path +'\\tools'):
                not_found_label = QLabel('Tools folder not found on the pipeline')
                self.team_tools_layout.addWidget(not_found_label,0,0)
                return
            
            scripts = []
            scenes = []

            for element in os.listdir(global_variables.pipeline_path +'\\tools'):
                
                if element.endswith('.py') or element.endswith('.mel'):
                    scripts.append(global_variables.fool_path +'\\tools\\'+element)
                if element.endswith('.ma') or element.endswith('.mb'):
                    scenes.append(global_variables.fool_path +'\\tools\\'+element)

            i = 0
            script_buttons_instances = {}
            for script in scripts:
                script_buttons_instances[script] = Drop_script_button(text=script.split('\\')[-1],parent=self,file=script)

                row = i // 5  
                column = i % 5   

                self.team_tools_layout.addWidget(script_buttons_instances[script], row, column)  
                i+=1
            
            scenes_buttons_instances = {}
            for scene in scenes:
                scenes_buttons_instances[scenes] = Drop_reference_button(text=scene.split('\\')[-1],parent=self,file=scene)

                row = i // 5  
                column = i % 5   

                self.team_tools_layout.addWidget(scenes_buttons_instances[scene], row, column)  
                i+=1
        
        set_my_tools()
        set_team_tools()

    def open_my_tools(self):
        pass

    def open_team_tools(self):
        pass
    
    def dragEnterEvent(self, e):
        e.accept()


class Drop_reference_button(QPushButton):
    '''
    A QPushButton allowing to drop references in a maya scene
    '''
    def __init__(self,text,parent,file):
        super().__init__()

        self.parent_widget= parent
        self.setText(text)
        self.file = file

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:

            drag = QDrag(self)
            mime = QMimeData()

            if not self.file:
                return
            #--- --- ---



            file_path_formatted = self.file.replace('\\','//').replace('//','/')
            print(file_path_formatted)


            maya_code = f'''
import maya.cmds as cmds

def onMayaDroppedPythonFile(*args):
    print('putain')
    file_path = '{file_path_formatted}'

    cmds.file(file_path, reference=True)
print('putain x2')


'''
            
            temp_file_name = f'temp_file_drop_{uuid.uuid4()}.py'
            temp_file_path = global_variables.fool_path + '\\temp\\' + temp_file_name 
            temp_file_path = temp_file_path.replace('\\','/')


            with open(temp_file_path, "w") as temp_file:
                temp_file.write(maya_code)


            mime.setUrls([QUrl.fromLocalFile(temp_file_path)])
            drag.setMimeData(mime)
            drag.exec()

            file_path = Path(temp_file_path)
            file_path.unlink()

class Drop_script_button(QPushButton):
    '''
    A QPushButton allowing to drop scripts in a maya scene
    '''
    def __init__(self,text,parent,file):
        super().__init__()

        self.parent_widget= parent
        self.setText(text)
        self.file = file

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:


            drag = QDrag(self)
            mime = QMimeData()

            if not self.file:
                return

            #--- --- ---
            with open(self.file, 'r') as file:
                script_content = file.read()
            file_path_formatted = self.file.replace('\\','//').replace('//','/')
            print(file_path_formatted)


            maya_code = f"""
import maya.cmds as cmds
import subprocess
def onMayaDroppedPythonFile(*args):
    exec('''{script_content}''')
"""
            temp_file_name = f'temp_file_drop_{uuid.uuid4()}.py'
            temp_file_path = global_variables.fool_path + '\\temp\\' + temp_file_name 
            temp_file_path = temp_file_path.replace('\\','/')


            with open(temp_file_path, "w") as temp_file:
                temp_file.write(maya_code)


            mime.setUrls([QUrl.fromLocalFile(temp_file_path)])
            drag.setMimeData(mime)
            drag.exec()

            file_path = Path(temp_file_path)
            file_path.unlink()

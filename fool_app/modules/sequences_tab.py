
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

#--- utilities
from .utilities import Buttons_gridLayout
#--- --- --- ---#

#--- Global vars
sequences_url = global_variables.sequences_url

response = requests.get(f'{sequences_url}/get_sequences_maya_departments')
sequences_maya_departments = response.json()

response = requests.get(f'{sequences_url}/get_sequences_houdini_departments')
sequences_houdini_departments = response.json()

response = requests.get(f'{sequences_url}/get_sequences_status')
sequences_status = response.json()

#--- --- --- ---#

class Sequences_tab(QWidget):
    def __init__(self):
        super().__init__()

        self.sequences_layout = QHBoxLayout()
        self.setLayout(self.sequences_layout)

        self.left_sublayout = QVBoxLayout()
        self.sequences_layout.addLayout(self.left_sublayout)
        self.right_sublayout = QHBoxLayout()
        self.sequences_layout.addLayout(self.right_sublayout)
        response = requests.get(url=f'{sequences_url}/get_sequences')
        sequences = response.json()
        #--- --- ---
        self.sequencesButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=6,borderVis=False,boxName='Sequences',checkable=True,
                                             buttons=sequences,clickConnect=[self.update_shots_view])
        self.left_sublayout.addWidget(self.sequencesButtons)

        #need to find a better name
        self.shots_view = Shots_widget(parent_class=self)
        self.left_sublayout.addWidget(self.shots_view)
        #--- --- ---
        self.tabWiget = QTabWidget()
        self.right_sublayout.addWidget(self.tabWiget)



        self.maya_tab = Software_subtab(software='maya',sequence=self.sequencesButtons,shot=self.shots_view,status_buttons=sequences_status,departments_buttons=sequences_maya_departments)
        self.tabWiget.addTab(self.maya_tab,'Maya tab')

        self.houdini_tab = Software_subtab(software='houdini',sequence=self.sequencesButtons,shot=self.shots_view,status_buttons=[],departments_buttons=sequences_houdini_departments)
        self.tabWiget.addTab(self.houdini_tab,'Houdini tab')
        
        

    '''def set_current_sequence(self):
        current_sequence = self.sequence_buttons_group.checkedButton().text()
        self.current_sequence = current_sequence'''

    #--- --- ---

    def update_shots_view(self):
        self.shots_view.set_listView()

    #--- --- ---

    def open_sequence(self):
        pass

    #--- --- ---

    def on_display(self):
        pass


class Shots_widget(QWidget):

    def __init__(self,parent_class):
        super().__init__()
        self.parent_class = parent_class

        self.shots_layout = QHBoxLayout()
        self.setLayout(self.shots_layout)

        #--- --- ---

        self.model = QStandardItemModel()
        self.set_listView()

        #--- --- ---

        self.listView = QListView()
        self.listView.setModel(self.model)
        self.shots_layout.addWidget(self.listView)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.clicked.connect(self.set_shot_selection)
        self.listView.doubleClicked.connect(self.open_shot)

        #--- --- ---

        self.shot_selection = None

        #--- --- --


    #--- --- ---

    def set_listView(self):
        'sets the listview with the shots of the selected sequence'

        self.model.clear()
        if not self.parent_class.sequencesButtons.currentButton:
            return
        
        response = requests.get(f'{global_variables.sequences_url}/get_shots/{self.parent_class.sequencesButtons.currentButton.text()}')
        shots = response.json()

        for shot in shots:
            item = QStandardItem(shot)
            self.model.appendRow(item)


    def set_shot_selection(self):
        'sets the shot selection to the selected item'
        index = self.listView.currentIndex()
        item = self.model.itemFromIndex(index)
        self.shot_selection = item.text()


    def open_shot(self):
        'opens the selected shot'
        response = requests.get(f'{global_variables.sequences_url}/get_shot_path/{self.parent_class.sequencesButtons.currentButton.text()}/{self.shot_selection}')
        shot_path = response.json()
        print(shot_path)
        os.startfile(shot_path)


class Software_subtab(QWidget):
    def __init__(self,
                 sequence,
                 shot,
                 software:str = 'Software',
                 status_buttons:list = None,
                 departments_buttons:list = None
                 ):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.listView = Files_tableView(parent_class=self,sequence=sequence,shot=shot)

        if departments_buttons:
            self.departmentsButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName='Departments',checkable=True,
                                                    buttons=departments_buttons,doubleClickConnect=[],clickConnect=[self.listView.set_tableView,self.set_current_department])
            layout.addWidget(self.departmentsButtons)
            self.current_department = None

        if status_buttons:
            self.statusButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName='Status',checkable=True,
                                                    buttons=status_buttons,doubleClickConnect=[],clickConnect=[self.listView.set_tableView,self.set_current_status])
            layout.addWidget(self.statusButtons)
            self.current_status = None

        layout.addWidget(self.listView)


    #--- --- ---

    def set_current_status(self):
        'returns current status'
        if hasattr(self,'statusButtons'):
            self.current_status = self.statusButtons.currentButton.text()
            return self.current_status
        return None
    
    #--- --- ---

    def set_current_department(self):
        'returns current department'
        if hasattr(self,'departmentsButtons'):
            self.current_department = self.departmentsButtons.currentButton.text()
            return self.current_department
        return None




class Files_tableView(QWidget):
    def __init__(self,parent_class,sequence,shot):
        super().__init__()

        self.parent_class = parent_class
        self.sequence = sequence
        self.shot = shot

        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Last Modification", "Comment"])
        
        self.listView = QTableView()
        layout.addWidget(self.listView)
        self.visualSettings()

    #--- --- ---

    def visualSettings(self):
        self.listView.setEditTriggers(QTableView.NoEditTriggers)
        self.listView.horizontalHeader().setStretchLastSection(True)
        self.listView.setShowGrid(False)
        self.listView.resizeRowsToContents()  
        self.listView.resizeColumnsToContents()

    #--- --- ---

    def set_tableView(self):

        sequence = self.sequence.currentButtonName()
        shot = self.shot.shot_selection
        status = self.parent_class.current_department
        department = self.parent_class.current_status
        print(sequence,status,department)
        response = requests.get(f'{global_variables.sequences_url}/get_files/{sequence}/{shot}/{department}/{status}')
        files = response.json()
        print(files)

    #--- --- ---

    '''def update_listview(self):
        self.active_software_tab = self.software_tab_widget.currentWidget()
        if not self.active_software_tab:
            return

        asset_type = self.active_asset_subtab.get_asset_type()
        asset_name = self.active_asset_subtab.get_asset_selection()

        department = self.active_software_tab.get_department()
        status = self.active_software_tab.get_status()

        if None in (asset_type, asset_name, department):
            return 
        
        #self.files_view_model.clear()
        self.files_view_model.removeRows(0, self.files_view_model.rowCount())

        response = requests.get(f'{base_url}/get_files_of_asset/{asset_type}/{asset_name}/{department}/{status}')
        results = response.json()

        for result in results:
            name = QStandardItem(result[0])
            last_modification = QStandardItem(result[1].split()[0])
            #comment = QStandardItem(result[2])
            #self.files_view_model.appendRow([name, last_modification, comment])
            self.files_view_model.appendRow([name, last_modification])

        print(results)
        self.files_view.resizeRowsToContents()
        self.files_view.resizeColumnsToContents()'''
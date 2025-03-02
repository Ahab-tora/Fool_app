
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
        self.sequencesButtons= Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=6,borderVis=False,boxName='Sequences',checkable=True,
                                             buttons=sequences,clickConnect=[self.update_shots_view])
        self.left_sublayout.addWidget(self.sequencesButtons)

        #need to find a better name
        self.shots_view = Shots_widget(parent_class=self)
        self.left_sublayout.addWidget(self.shots_view)
        #--- --- ---
        self.tabWiget = QTabWidget()
        self.right_sublayout.addWidget(self.tabWiget)



        self.maya_tab = Software_subtab(software='maya',status_buttons=sequences_status,departments_buttons=sequences_maya_departments)
        self.tabWiget.addTab(self.maya_tab,'Maya tab')

        self.houdini_tab = Software_subtab(software='houdini',status_buttons=[],departments_buttons=sequences_houdini_departments)
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
                 software:str = 'Software',
                 status_buttons:list = None,
                 departments_buttons:list = None,
                 ):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        if departments_buttons:
            self.departmentsButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName='Departments',checkable=True,
                                                    buttons=departments_buttons,doubleClickConnect=[],clickConnect=[])
            layout.addWidget(self.departmentsButtons)

        if status_buttons:
            self.statusButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName='Status',checkable=True,
                                                    buttons=status_buttons,doubleClickConnect=[],clickConnect=[])
            layout.addWidget(self.statusButtons)

        
        self.listView = Files_listView()
        layout.addWidget(self.listView)


class Files_listView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.listView = QListView()
        layout.addWidget(self.listView)
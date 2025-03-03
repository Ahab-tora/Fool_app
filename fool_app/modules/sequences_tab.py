
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

response = requests.get(f'{sequences_url}/get_sequences_path')
sequences_path = response.json()

response = requests.get(f'{sequences_url}/get_sequences_maya_departments')
sequences_maya_departments = response.json()

response = requests.get(f'{sequences_url}/get_sequences_houdini_departments')
sequences_houdini_departments = response.json()

response = requests.get(f'{sequences_url}/get_sequences_status')
sequences_status = response.json()

#--- --- --- ---#

class Sequences_tab(QWidget):
    def __init__(self):
        'main tab for the sequences managment'
        super().__init__()

        #--- --- --- Layout
        self.sequences_layout = QHBoxLayout()
        self.setLayout(self.sequences_layout)

        self.left_sublayout = QVBoxLayout()
        self.sequences_layout.addLayout(self.left_sublayout)
        self.right_sublayout = QHBoxLayout()
        self.sequences_layout.addLayout(self.right_sublayout)
        

        #--- --- ---  Left side with sequences and shots view

        response = requests.get(url=f'{sequences_url}/get_sequences')
        sequences = response.json()

        self.sequencesButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,borderVis=False,boxName='Sequences',checkable=True,
                                             buttons=sequences,clickConnect=[self.update_shots_view,self.update_files],maximumHeight=200,maximumWidth=350,
                                             font='Times',fontSize=10)
        self.sequencesButtons.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.left_sublayout.addWidget(self.sequencesButtons)

        openSequenceButton = QPushButton('Open sequence')
        openSequenceButton.clicked.connect(self.open_sequence)
        self.left_sublayout.addWidget(openSequenceButton)

        #need to find a better name
        self.shots_view = Shots_widget(parent_class=self)
        self.left_sublayout.addWidget(self.shots_view)

        #--- --- --- softwares tabs

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabWidget.currentChanged.connect(self.set_activeSoftwareTab)
        self.right_sublayout.addWidget(self.tabWidget)

        self.maya_tab = Software_subtab(software='maya',sequence=self.sequencesButtons,shot=self.shots_view,status_buttons=sequences_status,departments_buttons=sequences_maya_departments)
        self.tabWidget.addTab(self.maya_tab,'Maya tab')

        self.activeSoftwareTab = self.maya_tab

        self.houdini_tab = Software_subtab(software='houdini',sequence=self.sequencesButtons,shot=self.shots_view,status_buttons=[],departments_buttons=sequences_houdini_departments)
        self.tabWidget.addTab(self.houdini_tab,'Houdini tab')

        self.sequences_layout.setStretch(0, 3)  
        self.sequences_layout.setStretch(1, 7)  
        
    #--- --- ---

    def update_files(self):
        self.activeSoftwareTab.filesView.set_tableView()

    #--- --- ---

    def set_activeSoftwareTab(self):
        'changes the activeSoftwareTab to the current selection'
        self.activeSoftwareTab = self.tabWidget.currentWidget()
        
    #--- --- ---

    def update_shots_view(self):
        'updates the shots view'
        self.shots_view.set_listView()

    #--- --- ---

    def open_sequence(self):
        'opens the folder of the selected sequence'
        try:
            currentSequence = self.sequencesButtons.currentButtonName()
            print(currentSequence)
            if not currentSequence:
                return
            sequence_path = sequences_path + '\\' + currentSequence
            print(sequence_path)
            os.startfile(sequence_path)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed open the sequence folder:{e}")

    #--- --- ---

    def on_display(self):
        pass

#---  ---#

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
        self.listView.setMaximumWidth(350)
        self.listView.setModel(self.model)
        self.shots_layout.addWidget(self.listView)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.clicked.connect(self.set_shot_selection)
        self.listView.clicked.connect(self.parent_class.update_files)
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

#---  ---#

class Software_subtab(QWidget):
    def __init__(self,
                 sequence,
                 shot,
                 software:str = 'Software',
                 status_buttons:list = None,
                 departments_buttons:list = None,
                 departmentToStatusPath:str = None,
                 ):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        
        
        self.filesView = Files_tableView(parent_class=self,sequence=sequence,shot=shot)

        if departments_buttons:
            self.departmentsButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName='Departments',checkable=True,
                                                    buttons=departments_buttons,clickConnect=[self.filesView.set_tableView,self.set_current_department],
                                                    maximumHeight=70,fontSize=10)
            layout.addWidget(self.departmentsButtons)
            self.current_department = None

            self.openDepartmentButton = QPushButton('open department')
            self.openDepartmentButton.clicked.connect(self.openDepartment)


        if status_buttons:
            self.statusButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName='Status',checkable=True,
                                                    buttons=status_buttons,clickConnect=[self.filesView.set_tableView,self.set_current_status],
                                                    maximumHeight=70,fontSize=10)
            layout.addWidget(self.statusButtons)
            self.current_status = None

            self.openStatusButton = QPushButton('open status')
            self.openStatusButton.clicked.connect(self.openStatus)

        #--- ---

        self.openButtonsBox = QGroupBox()
        self.openButtonsBoxLayout = QHBoxLayout()
        self.openButtonsBox.setLayout(self.openButtonsBoxLayout)
        if departments_buttons:
            self.openButtonsBoxLayout.addWidget(self.openDepartmentButton)
        if status_buttons:
           self.openButtonsBoxLayout.addWidget(self.openStatusButton)
        layout.addWidget(self.openButtonsBox)

        layout.addWidget(self.filesView)

    #--- --- ---

    def openStatus(self):
        pass

    #--- --- ---

    def openDepartment(self):
        pass

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

#---  ---#

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
        
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.doubleClicked.connect(self.open_file)
        layout.addWidget(self.tableView)
        self.visualSettings()
        
        self.testButton = QPushButton('test')
        self.testButton.clicked.connect(self.addComment)
        layout.addWidget(self.testButton)

    def addComment(self):
        index = self.tableView.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        sequence = self.sequence.currentButtonName()
        shot = self.shot.shot_selection
        if hasattr(self.parent_class,'current_status'):
            status = self.parent_class.current_status
        else:
            status = None
        department = self.parent_class.current_department
        if None in [sequence,shot,department]:
            return
        
        comment='testComment'
        
        requests.post(f'{sequences_url}/add_comment/{sequence}/{shot}/{department}/{status}/{file}/{comment}')
        

    #--- --- ---

    def open_file(self):

        index = self.tableView.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        sequence = self.sequence.currentButtonName()
        shot = self.shot.shot_selection
        if hasattr(self.parent_class,'current_status'):
            status = self.parent_class.current_status
        else:
            status = None
        department = self.parent_class.current_department
        if None in [sequence,shot,department]:
            return

        response = requests.get(f'{sequences_url}/get_file_path/{sequence}/{shot}/{department}/{status}/{file}')
        file_path = response.json()
        
        os.startfile(file_path)

    #--- --- ---

    def visualSettings(self):
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(False)
        self.tableView.resizeRowsToContents()  
        self.tableView.resizeColumnsToContents()
        self.tableView.verticalHeader().hide()

    #--- --- ---

    def set_tableView(self):

        sequence = self.sequence.currentButtonName()
        shot = self.shot.shot_selection
        if hasattr(self.parent_class,'current_status'):
            status = self.parent_class.current_status
        else:
            status = None
        department = self.parent_class.current_department
        if None in [sequence,shot,department]:
            return

        response = requests.get(f'{global_variables.sequences_url}/get_files/{sequence}/{shot}/{status}/{department}')
        files = response.json()

        #self.files_view_model.clear()
        self.model.removeRows(0, self.model.rowCount())


        for data in files:
            name = QStandardItem(data[0])
            last_modification = QStandardItem(data[1].split()[0])
            #comment = QStandardItem(result[2])
            #self.files_view_model.appendRow([name, last_modification, comment])
            self.model.appendRow([name, last_modification])
        self.visualSettings()


    #--- --- ---

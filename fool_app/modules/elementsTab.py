#--- --- Imports

#--- PySide6 imports

from PySide6.QtWidgets import QButtonGroup,QRadioButton,QAbstractItemView,QHBoxLayout,QListView,QWidget,QLineEdit,QVBoxLayout,QPushButton,QTabWidget,QGroupBox,QDialogButtonBox,QDialog,QLabel,QTableView,QHeaderView
from PySide6.QtWidgets import  QGridLayout, QWidget, QVBoxLayout,QPushButton,QLineEdit, QMessageBox,QSizePolicy
from PySide6.QtGui import QStandardItemModel,QStandardItem,QDrag
from PySide6.QtCore import Qt,QMimeData,QUrl

#--- Standard library imports
import os,shutil,sqlite3,logging,uuid,requests,pprint
from pathlib import Path
from typing import Callable, Optional


#--- data imports

import data
from data import global_variables

#--- utilities
from .utilities import Buttons_gridLayout
#--- --- --- ---#


class ElementsTab(QWidget):
    def __init__(self,name):
        'main tab to manage elements'
        super().__init__()

        self.name = name

        #--- --- --- Layout
        self.typesLayout = QHBoxLayout()
        self.setLayout(self.typesLayout)

        self.left_sublayout = QVBoxLayout()
        self.typesLayout.addLayout(self.left_sublayout)
        self.right_sublayout = QVBoxLayout()
        self.typesLayout.addLayout(self.right_sublayout)
        

        #--- --- ---  Left side with types and roots view

        response = requests.get(url=f'{global_variables.queryUrl}/getTypes/{self.name}')
        types = response.json()

        self.elementsButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,borderVis=False,boxName='Types',checkable=True,
                                             buttons=types,clickConnect=[self.update_rootsView,self.updateFiles],maximumHeight=200,maximumWidth=350,
                                             font='Times',fontSize=10)
        self.elementsButtons.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.left_sublayout.addWidget(self.elementsButtons)

        openTypesButton = QPushButton('Open type')
        openTypesButton.clicked.connect(self.openType)
        self.left_sublayout.addWidget(openTypesButton)

        #need to find a better name
        self.rootsView = RootsWidget(parent_class=self)
        self.left_sublayout.addWidget(self.rootsView)

        #--- --- --- softwares tabs

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabWidget.currentChanged.connect(self.set_activeSoftwareTab)
        self.right_sublayout.addWidget(self.tabWidget)

        #request config
        #tab for each first element
        #build from here
        response = requests.get(f'{global_variables.queryUrl}/getConfig/{self.name}')
        config = response.json()
        pprint.pp(config)
        '''self.mayaDepartmentConfig = SoftwareFolderData(folderName='departments',buttons=sequences_maya_departments,changeConnect=[self.updateFiles])
        self.mayaStatusConfig =  SoftwareFolderData(folderName='status',buttons=sequences_status,changeConnect=[self.updateFiles])
        self.mayaTab = Software_subtab(softwaresFolderData=[self.mayaDepartmentConfig,self.mayaStatusConfig],
                                       basePath= lambda : sequences_path + '\\' + self.currentSequence() + '\\' + self.currentRoot() or '')

        self.tabWidget.addTab(self.mayaTab,'Maya tab')
        self.activeSoftwareTab = self.mayaTab

        self.typesLayout.setStretch(0, 3)  
        self.typesLayout.setStretch(1, 7)  '''
        
        #--- --- --- Files view

        ''' self.filesView = Files_tableView(parent_class=self,dbType='test',dbName=self.currentSequence,element=self.currentRoot,department=self.currentDepartment,status=self.currentStatus)
        self.right_sublayout.addWidget(self.filesView)'''
    #--- --- ---

    def updateFiles(self):
        self.filesView.set_tableView()

    #--- --- ---

    def set_activeSoftwareTab(self):
        'changes the activeSoftwareTab to the current selection'
        self.activeSoftwareTab = self.tabWidget.currentWidget()
        
    #--- --- ---

    def update_rootsView(self):
        'updates the shots view'
        self.rootsView.set_listView()

    #--- --- ---

    def currentSequence(self):
        if self.elementsButtons.currentButtonName():
            return self.elementsButtons.currentButtonName()
        return None

    #--- --- ---

    def currentShot(self):
        if self.rootsView.currentShot:
            return self.rootsView.currentShot
        return None

    #--- --- ---

    def currentDepartment(self):
        return self.activeSoftwareTab.folders['departments']['currentValue']()
    
    #--- --- ---

    def currentStatus(self):
        return self.activeSoftwareTab.folders['status']['currentValue']()
    
    #--- --- ---
    def openType(self):
        'opens the folder of the selected sequence'
        try:
            currentSequence = self.elementsButtons.currentButtonName()
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

class RootsWidget(QWidget):

    def __init__(self,parent_class):
        super().__init__()
        self.parent_class = parent_class

        self.rootsLayout = QHBoxLayout()
        self.setLayout(self.rootsLayout)

        #--- --- ---

        self.model = QStandardItemModel()
        self.set_listView()

        #--- --- ---

        self.listView = QListView()
        self.listView.setMaximumWidth(350)
        self.listView.setModel(self.model)
        self.rootsLayout.addWidget(self.listView)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.clicked.connect(self.setRootSelection)
        self.listView.clicked.connect(self.parent_class.updateFiles)
        self.listView.doubleClicked.connect(self.openRoot)

        #--- --- ---

        self.currentRoot = None

        #--- --- --


    #--- --- ---

    def set_listView(self):
        'sets the listview with the shots of the selected sequence'

        self.model.clear()
        if not self.parent_class.elementsButtons.currentButton:
            return

        response = requests.get(f'{global_variables.queryUrl}/getRoots/{self.parent_class.currentSequence()}')
        roots = response.json()

        for root in roots:
            item = QStandardItem(root)
            self.model.appendRow(item)


    def setRootSelection(self):
        'sets the shot selection to the selected item'
        index = self.listView.currentIndex()
        item = self.model.itemFromIndex(index)
        self.currentRoot = item.text()


    def openRoot(self):
        'opens the selected shot'
        response = requests.get(f'{global_variables.sequences_url}/get_shot_path/{self.parent_class.elementsButtons.currentButton.text()}/{self.currentRoot}')
        shot_path = response.json()
        print(shot_path)
        os.startfile(shot_path)




class SoftwareFolderData():
    def __init__(self,
                 folderName:str,
                 buttons:list,
                 inPath:str = None,
                 outPath:str = None,
                 changeConnect:list[Callable] = []
                 ):
        self.folderName =folderName
        self.buttons = buttons
        self.inPath = inPath
        self.outPath = outPath
        self.changeConnect = changeConnect

#--- ---  ---#

class Software_subtab(QWidget):
    '''
    Widget to display the departments and status for a given software as buttons, allow to quickly acces the path of these departments,
    Displays a view of the files
    '''
    
    def __init__(self,
                 softwaresFolderData:list[SoftwareFolderData],
                 basePath:str
                 ) :

        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.basePath = basePath
        
        self.folders = {}
        self.openButtons = []

        for folder in softwaresFolderData:

            self.folders[folder.folderName] = {}
            self.folders[folder.folderName]['dataClass'] = folder
           

            self.folders[folder.folderName]['buttons'] = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,
                                                    borderVis=True,boxName=folder.folderName,checkable=True,
                                                    buttons=folder.buttons,clickConnect=[func for func in folder.changeConnect],
                                                    maximumHeight=70,fontSize=10)
            
            self.folders[folder.folderName]['openButton'] = QPushButton(f'Open {folder.folderName}')
            self.folders[folder.folderName]['openButton'].clicked.connect(lambda checked=True, folder = self.folders[folder.folderName] : self.open(checked=checked,folder = folder))
            self.openButtons.append(self.folders[folder.folderName]['openButton'])
            
            layout.addWidget(self.folders[folder.folderName]['buttons'])

            self.folders[folder.folderName]['currentValue'] = lambda folderName=folder.folderName: self.folders[folderName]['buttons'].currentButton.text()


        self.openButtonsBox = QGroupBox()
        self.openButtonsBoxLayout = QHBoxLayout()
        self.openButtonsBox.setLayout(self.openButtonsBoxLayout)
        for openButton in self.openButtons:
            self.openButtonsBoxLayout.addWidget(openButton)

        layout.addWidget(self.openButtonsBox)

    def open(self,checked,folder):
        print('uh')
        print(self.basePath())
        print(folder['departments']['currentValue']())
        #self.folders[folder]['departments']

        #folderName = self.folders[folder]['departments']['currentValue']()
        #os.startfile(os.path.join(self.basePath(),inPath or '',folderName,outPath or ''))
        
        
#--- ---  ---#

class Files_tableView(QWidget):
    def __init__(self,
                 parent_class,dbType:str,
                 dbName:Callable[[], str],element:Callable[[], str],
                 department:Callable[[], str],status:Callable[[], str]):
        
        super().__init__()
        #--- --- ---

        self.parent_class = parent_class
        self.dbType = dbType
        self.dbName = dbName
        self.element = element
        self.department = department
        self.status = status

        #--- --- ---

        layout = QHBoxLayout()
        self.setLayout(layout)
        
        #--- --- ---

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Last Modification", "Comment"])
        self.selectedFile = None

        #--- --- ---

        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.clicked.connect(self.setSelectedFile)
        self.tableView.doubleClicked.connect(self.open_file)
        layout.addWidget(self.tableView)
        self.visualSettings()
        
        #--- --- ---

        self.testButton = QPushButton('test')
        self.testButton.clicked.connect(self.addComment)
        layout.addWidget(self.testButton)

    def setSelectedFile(self):
        
        index = self.tableView.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        self.selectedFile = file

    def addComment(self):

        pass
        '''
        index = self.tableView.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        sequence = self.dbName.currentButtonName()
        shot = self.shot.shot_selection
        if hasattr(self.parent_class,'current_status'):
            status = self.parent_class.current_status
        else:
            status = None
        department = self.parent_class.current_department
        if None in [sequence,shot,department]:
            return
        
        comment='testComment'
        
        requests.post(f'{sequences_url}/add_comment/{sequence}/{shot}/{department}/{status}/{file}/{comment}')'''
        

    #--- --- ---

    def open_file(self):

        '''index = self.tableView.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        sequence = self.dbName.currentButtonName()
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
        
        os.startfile(file_path)'''

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

        print(self.dbName(),self.element(),self.status(),self.department())
        response = requests.get(f'{global_variables.sequences_url}/get_files/{self.dbName()}/{self.element()}/{self.status()}/{self.department()}')
        files = response.json()

        self.model.removeRows(0, self.model.rowCount())

        for data in files:
            name = QStandardItem(data[0])
            last_modification = QStandardItem(data[1].split()[0])
            comment = QStandardItem(data[2])
            self.model.appendRow([name, last_modification,comment])
        self.visualSettings()


    #--- --- ---

#--- --- Imports

#--- PySide6 imports

from PySide6.QtWidgets import QButtonGroup,QAbstractItemView,QHBoxLayout,QListView,QWidget,QLineEdit,QVBoxLayout,QPushButton,QTabWidget,QGroupBox,QTableView,QHeaderView
from PySide6.QtWidgets import QWidget, QVBoxLayout,QPushButton,QLineEdit, QMessageBox,QSizePolicy,QMenu
from PySide6.QtGui import QStandardItemModel,QStandardItem,QDrag,QClipboard
from PySide6.QtCore import Qt,QMimeData,QUrl,QAbstractItemModel,QAbstractTableModel,QModelIndex

#--- Standard library imports
import os,shutil,logging,uuid,requests,time
from pathlib import Path
from typing import Callable


#--- data imports
import data
from data import global_variables

#--- utilities
from .utilities import Buttons_gridLayout,doubleClickButton
#--- --- --- ---#

fool_path = global_variables.fool_path

class ElementsTab(QWidget):
    def __init__(self,name):
        'main tab to manage elements'
        super().__init__()

        self.name = name
        self.parentPath =''

        #--- --- --- Layout
        #main layout
        self.typesLayout = QHBoxLayout()
        self.setLayout(self.typesLayout)

        #left layout with the types and roots
        self.left_sublayout = QVBoxLayout()
        self.typesLayout.addLayout(self.left_sublayout)

        #right layout with subelements buttons and files view
        self.right_sublayout = QVBoxLayout()
        self.typesLayout.addLayout(self.right_sublayout)
        

        #--- --- ---  Left side with types and roots view

        response = requests.get(url=f'{global_variables.queryUrl}/getTypes/{self.name}')
        types = response.json()
        response = requests.get(url=f'{global_variables.queryUrl}/getElementPath/{self.name}')
        self.inputPath = response.json()
        
        self.elementsButtons = Buttons_gridLayout(mutually_exclusive=True,buttonsPerRow=5,borderVis=False,boxName='Types',checkable=True,
                                             buttons=types,clickConnect=[self.update_rootsView,self.updateFiles],
                                             maximumHeight=200,maximumWidth=350,
                                             font='Times',fontSize=10)
        self.elementsButtons.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.left_sublayout.addWidget(self.elementsButtons)


        openTypesButton = QPushButton('Open type')
        openTypesButton.clicked.connect(self.openType)
        self.left_sublayout.addWidget(openTypesButton)

        #need to find a better name
        self.rootsView = RootsWidget(parentClass=self)
        self.left_sublayout.addWidget(self.rootsView)

        #--- --- --- softwares tabs

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.tabWidget.currentChanged.connect(self.set_activeSoftwareTab)
        self.right_sublayout.addWidget(self.tabWidget)

        response = requests.get(f"{global_variables.queryUrl}/getConfig/{self.name}")
        config = response.json()

        self.folderSubtabs = {}
        self.activefolderSubtab = None

        for key in config:
            self.folderSubtabs[key['name']] = FoldersSubTab(config=key,parentClass=self,basePath= '')
            self.tabWidget.addTab(self.folderSubtabs[key['name']],key['name'])
            self.activefolderSubtab = self.folderSubtabs[key['name']]


    
        self.tabWidget.currentChanged.connect(lambda changeActiveFolder : self.setActivefolderSubtab())
        self.setActivefolderSubtab()
        self.tabWidget.currentChanged.connect(lambda updateFiles : self.updateFiles())

        #--- --- --- Files view
        self.filesView = Files_tableView(dbName = self.getCurrentType,parentClass=self,parentPath=None)
        self.right_sublayout.addWidget(self.filesView)

        #right layout stretch
        self.right_sublayout.setStretch(0,3)
        self.right_sublayout.setStretch(1,7)

    #--- --- ---

    def setActivefolderSubtab(self):
        self.activefolderSubtab = self.tabWidget.currentWidget()
        self.setParentPath()

    #--- --- ---

    def getCurrentType(self):
        if self.elementsButtons.currentButtonName():
            return self.elementsButtons.currentButtonName()
        return None

    #--- --- ---

    def setParentPath(self):
        if None in [self.inputPath,self.getCurrentType(),self.rootsView.currentRoot,self.activefolderSubtab.selectedPath]:
            return None
        
        self.parentPath = os.path.join(self.inputPath,self.getCurrentType(),self.rootsView.currentRoot,self.activefolderSubtab.selectedPath).rstrip(os.sep)
        print(self.parentPath)
        return self.parentPath

    #--- --- ---

    def getParentPath(self):
        if self.parentPath:
            return self.parentPath
        return None
    
    #--- --- ---

    def updateFiles(self):
        print('updating')
        self.setParentPath()
        self.filesView.setTableView()

    #--- --- ---

    def update_rootsView(self):
        'updates the shots view'
        self.rootsView.setListView()

    #--- --- ---

    def openType(self):
        'opens the folder of the selected sequence'
        try:
            currentType = os.path.join(self.inputPath,self.getCurrentType())
            #print(currentType)
            os.startfile(currentType)

        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open:{e}")

    #--- --- ---

    def on_display(self):
        pass




class RootsWidget(QWidget):
    '''
    Listview with all the roots items from a type
    '''
    def __init__(self,parentClass):
        
        super().__init__()
        self.parentClass = parentClass

        self.rootsLayout = QVBoxLayout()
        self.setLayout(self.rootsLayout)

        self.searchBox = QLineEdit()
        self.searchBox.textChanged.connect(lambda text: self.setListViewSearch(search=text))
        self.rootsLayout.addWidget(self.searchBox)


        #--- --- ---

        self.model = QStandardItemModel()
        self.setListView()

        #--- --- ---

        self.listView = QListView()
        self.listView.setMaximumWidth(350)
        self.listView.setModel(self.model)
        self.rootsLayout.addWidget(self.listView)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.clicked.connect(self.setRootSelection)

        self.listView.clicked.connect(self.parentClass.updateFiles)
        self.listView.doubleClicked.connect(self.openRoot)

        #--- --- ---

        self.currentRoot = None

        #--- --- --


    #--- --- ---

    def setListView(self):
        'sets the listview with the shots of the selected sequence'

        self.model.clear()
        if not self.parentClass.elementsButtons.currentButton:
            return

        response = requests.get(f'{global_variables.queryUrl}/getRoots/{self.parentClass.getCurrentType()}')
        roots = response.json()

        for root in roots:
            item = QStandardItem(root)
            self.model.appendRow(item)
        
    #--- --- ---

    def setListViewSearch(self,search):
        'sets the listview with the shots of the selected sequence from search'

        self.model.clear()
        if not self.parentClass.elementsButtons.currentButton:
            return

        params = {'search':search}
        response = requests.get(f'{global_variables.queryUrl}/getRootsSearch/{self.parentClass.getCurrentType()}',params=params)
        roots = response.json()
        print(roots)
        for root in roots:
            item = QStandardItem(root)
            self.model.appendRow(item)

    #--- --- ---

    def setRootSelection(self):
        'sets the shot selection to the selected item'
        index = self.listView.currentIndex()
        item = self.model.itemFromIndex(index)
        self.currentRoot = item.text()

    #--- --- ---

    def openRoot(self):
        'opens the selected root'
        try:
            rootPath = os.path.join(self.parentClass.inputPath,self.parentClass.getCurrentType(),self.currentRoot)
            os.startfile(rootPath)
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not open:{e}")


#--- ---  ---#

class FoldersSubTab(QWidget):
    '''
    Allows to display checkable buttons with children to recreate a folder hierachy using a config file
    '''
    
    def __init__(self,
                 parentClass:Callable,
                 config:dict,
                 basePath:str
                 ) :

        super().__init__()
        
        self.parentClass = parentClass
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.basePath = basePath
        
        self.folders = {}
        self.openButtons = []

        self.selectedPath = ''

        buttonsDict = {}
        def addElements(config:dict,parentLayout,buttonsDict:dict,vis:bool=False,box=None,boxLayout=None,group=None,inheritedPath:str = ''):

            button = doubleClickButton(text=config['name'])
            button.setCheckable(True)
            button.setStyleSheet(f'''QPushButton:checked {{ background-color: #5288B2; }}''')
            button.setVisible(vis)
            button.setChecked(True)
            button.setAutoExclusive(True) 
            
            path = os.path.join(inheritedPath , config['inPath'] ,config['outPath'])

            button.clicked.connect(lambda: self.setPath(path=path))
            
            button.clicked.connect(lambda: self.parentClass.updateFiles())

            button.doubleClicked.connect(lambda:self.open(path=self.parentClass.getParentPath()))

            if box :
                boxLayout.addWidget(button)
                group.addButton(button)

            else:
                parentLayout.addWidget(button)

            if config['childrenElements']:

                buttonsDict[config['name']] = {}
                childButtonsDict = buttonsDict[config['name']]
                childButtonsDict['children'] = {}

                
                childButtonsDict['box'] = QGroupBox()
                childButtonsDict['box'].setStyleSheet("QGroupBox { border: none; }")

                childButtonsDict['layout'] = QHBoxLayout()
                childButtonsDict['box'].setLayout(childButtonsDict['layout'])
                parentLayout.addWidget(childButtonsDict['box'])

                childButtonsDict['buttonGroup'] = QButtonGroup()
                childButtonsDict['buttonGroup'].setExclusive(True)

                childButtonsDict['parentLayout'] = QHBoxLayout()
                
                parentLayout.addLayout(childButtonsDict['parentLayout'])

                
                for childConfig in config['childrenElements']:

                    addElements(config=childConfig,parentLayout=childButtonsDict['parentLayout'],vis=True,buttonsDict=childButtonsDict['children'],
                                box=childButtonsDict['box'] ,boxLayout=childButtonsDict['layout'],group=childButtonsDict['buttonGroup'],inheritedPath=path)
                
                childButtonsDict['buttonGroup'].buttonClicked.connect(lambda button: self.showChildren(buttonsDict=childButtonsDict['children'],buttonClicked=button.text()))
                self.showChildren(buttonsDict=childButtonsDict['children'],buttonClicked=button.text())

        addElements(config=config,buttonsDict=buttonsDict,parentLayout=layout,vis=True,inheritedPath=basePath)

    #--- --- ---

    def showChildren(self,buttonsDict:dict,buttonClicked):
        '''sets the visibility for children folders'''
        for buttonName in buttonsDict.keys():
            if not buttonName == buttonClicked:
                buttonsDict[buttonName]['box'].setVisible(False)
            else:
                buttonsDict[buttonName]['box'].setVisible(True)

    #--- --- ---

    def setPath(self,path):
        '''sets the selected path'''
        self.selectedPath = path

    #--- --- ---

    def path(self):
        return self.selectedPath

    #--- --- ---

    def open(self,path):
        
        if not os.path.exists(path):
            QMessageBox.warning(None, "Error", f'Could not open this path:{path}.')
            return

        os.startfile(path)

        
#--- ---  ---#

class contextMenuTableView(QTableView):
    '''tableView with custom actions'''

    def __init__(self,parentClass):
        super().__init__()
        self.parentClass = parentClass
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QTableView.DropOnly) 

    #--- --- ---

    def contextMenuEvent(self, event):

        menu = QMenu(self)

        openFileButton = menu.addAction("Open file")
        openFileSetProjectButton = menu.addAction('Open and set project')
        copyPath = menu.addAction("Copy path")
        copyFile = menu.addAction('Copy file')
        pasteFile = menu.addAction('Paste File')
        copyFileToDekstopButton = menu.addAction("Copy file to dekstop")
        refreshButton = menu.addAction('Refresh view')

        openFileButton.triggered.connect(self.openFile)
        openFileSetProjectButton.triggered.connect(self.openFileSetProject)
        copyPath.triggered.connect(self.copyPath)
        copyFile.triggered.connect(self.copyFile)
        pasteFile.triggered.connect(self.pasteFile)
        copyFileToDekstopButton.triggered.connect(self.copyFileToDekstop)
        refreshButton.triggered.connect(self.refreshView)

        selected_action = menu.exec(event.globalPos())
        #print('righyt click')

    #--- --- ---

    def openFile(self):

        if os.path.exists(self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath']):
            os.startfile(self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath'])

    #--- --- ---

    def  openFileSetProject(self):

        if not os.path.exists(self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath']):
            return
        
        currentRecursion = 0
        maxRecursion = 6 #limit of the recursion

        def checkWorkspace(path):

            parentDir = os.path.dirname(self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath'])
            folderDir = os.listdir(parentDir)

            if 'worspace.mel' in folderDir:
                print(folderDir)
                return
            
            currentRecursion += 1
            if currentRecursion == maxRecursion:
                return
            
            checkWorkspace(path = parentDir)
            
        checkWorkspace(path = self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath'] )

    #--- --- ---

    def copyPath(self):

        clipboard = QClipboard()
        path = self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath']
        clipboard.setText(path)

    #--- --- ---

    def copyFile(self):
        filePath = self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath']
        
        if not os.path.exists(filePath):
            return
        
        print(filePath)
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(filePath)])

        clipboard = QClipboard()
        clipboard.setMimeData(mime)

    #--- --- ---

    def pasteFile(self):
        clipboard = QClipboard()

        destPath = self.parentClass.parentClass.getParentPath()

        url = QUrl(clipboard.text())
        filePath = url.toLocalFile()
        print(filePath)
        if os.path.exists(filePath):
            shutil.copy(filePath,destPath)


    def copyFileToDekstop(self):

        filePath = self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath']
        if os.path.exists(filePath):
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
            destination = os.path.join(desktop, os.path.basename(filePath))

        if os.path.isfile(filePath):
            shutil.copy(filePath, destination)
        elif os.path.isdir(filePath):
            shutil.copytree(filePath, destination)

    #--- --- ---

    def refreshView(self):
        self.parentClass.setTableView()

    #--- --- ---

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    #--- --- ---

    def dragMoveEvent(self, event):
        print("dragMoveEvent")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    #--- --- ---

    def dropEvent(self,event):
        print(event)
        if event.mimeData().hasUrls():
          
            event.acceptProposedAction()
        
            for url in event.mimeData().urls():
                droppedFilePath = url.toLocalFile()
            
                destPath = self.parentClass.parentClass.getParentPath()
                shutil.copy(droppedFilePath,destPath)

                time.wait(1)
                self.refreshView()

        else:
            event.ignore()
            
    #--- --- ---

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()

            filePath = self.parentClass.itemsData[self.parentClass.selectedFileName]['fullPath'].replace('\\','//').replace('//','/')



            maya_code = f'''
import maya.cmds as cmds
def onMayaDroppedPythonFile(*args):
    filePath = '{filePath}'
    namespace = filePath.split('/')[-1][0:-3]
    cmds.file(filePath, reference=True,namespace=namespace)'''

            temp_file_name = f'temp_file_drop_{uuid.uuid4()}.py'
            temp_file_path = fool_path + '\\temp\\' + temp_file_name 
            temp_file_path = temp_file_path.replace('\\','/')


            with open(temp_file_path, "w") as temp_file:
                temp_file.write(maya_code)

            
            mime.setUrls([QUrl.fromLocalFile(temp_file_path)])
            drag.setMimeData(mime)
            drag.exec()

            file_path = Path(temp_file_path)
            file_path.unlink()

#--- ---  ---#

class FilesTableModel(QAbstractTableModel):


    def __init__(self,rows = [], columns = []):
        super().__init__()
        self.filesData = data
        self.rows = rows
        self.columns = columns
    

    def rowCount(self,parent):
        return len(self.rows)


    def columnCount(self, parent):
        return len(self.columns)


    def data(self, index, role):
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            return self.filesData[row][column]

    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            self.filesData[row][column] = float(value)
            self.dataChanged.emit(index, index)#データ変更シグナルを送出
            return True
        else:
            return False
        
#--- ---  ---#

class Files_tableView(QWidget):

    def __init__(self,
                 parentClass:Callable,
                 dbName:Callable[[], str],
                 parentPath:Callable[[],str]
                 ):
        
        super().__init__()
        #--- --- ---


        self.dbName = dbName
        self.parentPath = parentPath
        self.parentClass = parentClass

        #--- --- ---

        layout = QVBoxLayout()
        self.setLayout(layout)
        
                
        #--- --- ---

        self.searchBox = QLineEdit()
        self.searchBox.textChanged.connect(lambda text: self.setTableViewSearch(search=text))
        layout.addWidget(self.searchBox)

        #--- --- ---

        #self.model = FilesTableModel()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Last Modification", "Comment"])

        self.selectedFileName = None

        #--- --- ---

        self.tableView = contextMenuTableView(parentClass=self)
        self.tableView.setModel(self.model)
        self.tableView.clicked.connect(self.setSelectedFile)

        layout.addWidget(self.tableView)
        self.visualSettings()

    #--- --- ---

    def setSelectedFile(self):
        print('setting selected file')
        index = self.tableView.currentIndex()

        item = self.model.itemFromIndex(index)
        fileName = item.text()

        self.selectedFileName = fileName
        print(self.selectedFileName)

    #--- --- ---

    def addComment(self):

        pass
        '''
        index = self.tableView.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        sequence = self.dbName.currentButtonName()
        shot = self.shot.shot_selection
        if hasattr(self.parentClass,'current_status'):
            status = self.parentClass.current_status
        else:
            status = None
        department = self.parentClass.current_department
        if None in [sequence,shot,department]:
            return
        
        comment='testComment'
        
        requests.post(f'{sequences_url}/add_comment/{sequence}/{shot}/{department}/{status}/{file}/{comment}')'''
        
    #--- --- ---

    def visualSettings(self):
        #self.tableView.setEditTriggers(QTableView.NoEditTriggers)
        
        self.tableView.setShowGrid(False)
        self.tableView.resizeRowsToContents()  
        self.tableView.resizeColumnsToContents()
        self.tableView.verticalHeader().hide()
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    #--- --- ---

    def setTableView(self):

        params = {"parentPath": self.parentClass.getParentPath()}
        response = requests.get(url=f'{global_variables.queryUrl}/getFiles/{self.dbName()}',params=params)
        
        files = response.json()
        #print(files)
        self.model.removeRows(0, self.model.rowCount())

        self.itemsData = {}
        for data in files:

            self.itemsData[data[0]] = {'name':data[0],
                               'fullPath':data[1],
                               'type':data[2],
                               'size':data[3],
                               'lastModification':data[4],
                               'comment':data[5]}
        
            name = QStandardItem(data[0])
            fullPath = QStandardItem(data[1])
            type =QStandardItem(data[2])
            size =QStandardItem(data[3])
            lastModification = QStandardItem(data[4].split()[0])
            comment = QStandardItem(data[5])
            self.model.appendRow([name, lastModification,comment])

        self.visualSettings()

    #--- --- ---

    def setTableViewSearch(self,search):
        print('textChanged')
        params = {"parentPath": self.parentClass.getParentPath(),'search':search}
        response = requests.get(url=f'{global_variables.queryUrl}/getFilesSearch/{self.dbName()}',params=params)
        
        files = response.json()
        self.model.removeRows(0, self.model.rowCount())

        self.itemsData = {}
        for data in files:
            self.itemsData[data[0]] = {'name':data[0],
                               'fullPath':data[1],
                               'type':data[2],
                               'size':data[3],
                               'lastModification':data[4],
                               'comment':data[5]}
            
            name = QStandardItem(data[0])
            fullPath = QStandardItem(data[1])
            type =QStandardItem(data[2])
            size =QStandardItem(data[3])
            lastModification = QStandardItem(data[4].split()[0])
            comment = QStandardItem(data[5])
            
            self.model.appendRow([name, lastModification,comment])
            name.setFlags(name.flags() & ~Qt.ItemIsEditable)
            lastModification.setFlags(lastModification.flags() & ~Qt.ItemIsEditable)
            comment.setFlags(comment.flags() | Qt.ItemIsEditable)

        self.visualSettings()



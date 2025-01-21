#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import  QCheckBox,QGridLayout,QCheckBox, QWidget, QVBoxLayout, QLabel,QTreeView,QHeaderView,QFormLayout,QPushButton,QLineEdit
from PySide6.QtGui import QIcon,QFont,QColor
from PySide6.QtCore import QModelIndex,Qt,QAbstractItemModel

#--- Standart library imports
import logging,time,shutil,sqlite3,os,sys
from pathlib import Path

#--- data import

import data
from data import global_variables

#--- --- --- ---#

#logging.getLogger().setLevel(logging.DEBUG)
#logging.getLogger().setLevel(logging.CRITICAL + 1)



class Treeview(QWidget):
    '''
    widget to display the treeview in a QVBoxLayout
    '''
    def __init__(self,root_path,table_path):
        logging.debug('Launching Treeview __init__')
        super().__init__()

        self.treeview_tab_layout = QVBoxLayout()
        self.setLayout(self.treeview_tab_layout)
        print('-------------------',table_path)
        self.model = TreeModel(root_path=root_path,table_path=table_path)
    
        self.treeview_wgt = Treeview_SubClass(model =self.model)
        self.treeview_wgt.setModel(self.model)
        self.treeview_wgt.doubleClicked.connect(self.open_item)
        self.treeview_tab_layout.addWidget(self.treeview_wgt)

    def open_item(self,index):
        logging.debug('Launching open_item')
        #launches the selected item when double clicked
        
        index = self.treeview_wgt.selectionModel().selectedIndexes()[0]
        item = index.internalPointer()

        os.startfile(item.path_item)

class Treeview_SubClass(QTreeView):
    '''
    
    '''
    def __init__(self,model):
        super().__init__()
        logging.debug('Launching Treeview_SubClass __init__ ')

        self.model = model
        
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        treeview_font = QFont("Colibri", 10)  
        self.setFont(treeview_font)

        self.setAnimated(True)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)

    def dragEnterEvent(self, event):
        logging.debug('Launching dragEnterEvent')
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        logging.debug('Launching dragMoveEvent')
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self,event):
        logging.debug('Launching dropEvent')
        if event.mimeData().hasUrls():
          
            event.accept()
        
        # Process each file dropped
        for url in event.mimeData().urls():
            source_file_path = url.toLocalFile()
            
            target_index = self.indexAt(event.pos())
            item  = target_index.internalPointer()
            destination_file_path = item.data()

            if not os.path.isdir(destination_file_path):
                destination_file_path = os.path.split(destination_file_path)[0]
            shutil.copy(source_file_path,destination_file_path)
        # Implement file move/copy logic if needed
        else:
            event.ignore()


class TreeItem:

    #For each element of the scan, the class creates a TreeItem that will populate the treeview

    def __init__(self,item_data, parent=None):
        #We get the name, path,type,size,modification_date,creation_date,parent and children. self.is_loaded checks if the item already has been loaded in the treeview
        logging.debug('creating instance of TreeItem')

        self.name_item = item_data[1]
        self.path_item = item_data[2]
        self.type = item_data[3]
        self.size = item_data[4]
        self.modification_date = item_data[5]
        self.creation_date = item_data[6]
        self.parent_path = item_data[7]
        self.children_items = []
        self.parent_item = parent
        
        if  item_data[8] is None:
            self.children = None
        else:
            self.children = item_data[8].split(',')
 
    
        self.is_loaded = False  

    
    def append_child(self, child):
        logging.debug('Launching append_child')
        self.children_items.append(child)


    def insert_child(self, position, child):
        logging.debug('Launching insert_child')
        self.children_items.insert(position, child)


    def child(self, row):
        logging.debug('Launching child')
        return self.children_items[row]


    def path(self):
        logging.debug('Launching path')
        return self.path_item
    

    def name(self):
        logging.debug('Launching  name')
        return self.name_item
    

    def parent_path_(self):
        logging.debug('Launching parent_path')
        return self.parent_path
    

    def parent(self):
        logging.debug('Launching parent')
        return self.parent_item


    def row(self):
        logging.debug('Launching parent')
        if self.parent_path:
            return self.parent_item.children_items.index(self)
        return 0


    def is_directory(self):
        logging.debug('Launching is_directory')
        #Checks if the item is a directory, only directories can have children
        if self.type == 'folder':
            return True
        else:
            return False
 

    def find_item(self,looked_path):
        logging.debug('Launching find_item')

        if self.path_item == looked_path:
            return self

        for child in self.children_items:
            found_item = child.find_item(looked_path=looked_path)
            if found_item:
                return found_item


class TreeModel(QAbstractItemModel):
    #Custom model for the treeview, bypassing the issues of the remoteva servern
    def __init__(self, root_path, table_path,parent=None):
        super(TreeModel, self).__init__(parent)
        logging.debug('Launching treeview_model')

        self.table_path = table_path

        connection = sqlite3.connect(table_path)
        cursor=connection.cursor()
        root_id = 1
        query = '''SELECT * FROM treeview_table WHERE id = ?'''
        cursor.execute(query,(root_id,))
        data = cursor.fetchall()[0]
        print(data)
        self.root_item = TreeItem(item_data=data)
        

    def data(self, index, role=Qt.DisplayRole):
        logging.debug('launching data')

        if not index.isValid():
            return None
        item = index.internalPointer()

        #setting data
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.name_item
            elif index.column() == 1:
                return item.type
            elif index.column() == 2:
                return item.size
            elif index.column() == 3:
                return item.modification_date
            elif index.column() == 4:
                return item.creation_date
            
        #setting special font
        if role == Qt.FontRole:
            if item.type == "folder":
                bold_font = QFont()
                bold_font.setBold(True)
                return bold_font
            
        #settings colors
        if role == Qt.ForegroundRole :
            if item.type == "folder" and index.column() == 0:
                return QColor("white")  
            else:
                return QColor('lightGray')  
            
        #setting icons
        if role == Qt.DecorationRole and index.column() == 0:
            if item.type == 'folder':
                icon_path = global_variables.fool_path + '\\icons\\folder_icon.png'
                return QIcon(icon_path)


    def add_item_when_change(self,path):
        logging.debug('launch add_item_when_change')
        #when watchdog detects a change, populate the treeview with new items
        time.sleep(0.7)
        item = self.root_item.find_item(path)
        
        if item:
            parent_index = self.createIndex(item.row(), 0, item)
            self.fetchMore(parent=parent_index)


    def rowCount(self, parent=QModelIndex()):
        logging.debug("Launching rowCount")
        if parent.isValid():
            parent_item = parent.internalPointer()
        else:
            parent_item = self.root_item
        
        if parent_item.is_directory():
            if parent_item.children is not None:
                return len(parent_item.children)
            else:
                return 0


    def columnCount(self, parent=QModelIndex()):
        logging.debug('Launching columnCount')
        #Return the number of columns for the children of the given parent
        #name, type, size, creation_date, last_modification
        return 5
    

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        logging.debug('Launching headerData')
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Type"
            elif section == 2:
                return 'Size'
            elif section == 3:
                return 'Modification date'
            elif section == 4:
                return 'Creation date'
        return None
    

    def index(self, row, column, parent=QModelIndex()):
        logging.debug('Launching index')
        #Create and return an index for the given row, column, and parent

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)


        if child_item:
            logging.debug(f"Creating index with child item: {child_item}, {child_item.path()}")
            x = self.createIndex(row, column, child_item)
            
            return x
        return QModelIndex()


    def parent(self, index):
        logging.debug('Launching parent')
        #Return the parent of the item referred to by the given index

        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item or parent_item is None:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)
    

    def canFetchMore(self, parent):
        logging.debug('Launching canFetchMore')
        #Indicates whether there is more data to fetch for the given parent

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if parent_item.is_loaded:
            return False
        # If the item is a directory and hasn't been loaded yet
        if parent_item.is_directory():
            return True
        return parent_item.is_directory() and not parent_item.is_loaded


    def fetchMore(self, parent):
        logging.debug('fetchmore')

        if not parent.isValid():
            parent_item = self.root_item

        else:
            parent_item = parent.internalPointer()

        if parent_item.is_loaded:
            return

        if not parent_item.children:

            return
        
        parent_item.is_loaded = True
        
        connection = sqlite3.connect(self.table_path)
        cursor = connection.cursor()

        placeholder = '?'
        for x in range(len(parent_item.children)-1):
            placeholder = placeholder +','+ '?'
            
        query =f''' SELECT * FROM treeview_table WHERE id IN ({placeholder})'''
        cursor.execute(query,parent_item.children)
        children_data = cursor.fetchall()
            
        connection.close()

        for data in children_data:
                
            child_item = TreeItem(item_data=data, parent=parent_item)
            parent_item.append_child(child_item)

        self.beginInsertRows(parent, 0, len(parent_item.children_items) - 1)
        self.endInsertRows()



        
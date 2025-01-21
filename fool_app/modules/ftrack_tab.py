#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QWidget,QLineEdit,QVBoxLayout,QPushButton,QLabel,QTabWidget,QTreeView,QHeaderView,QStyledItemDelegate,QComboBox,QGroupBox
from PySide6.QtWidgets import  QCheckBox,QGridLayout,QCheckBox, QWidget, QVBoxLayout, QLabel,QTreeView,QHeaderView,QPushButton,QLineEdit, QMessageBox
from PySide6.QtGui import QFont,QColor
from PySide6.QtCore import QModelIndex,Qt,QAbstractItemModel

#--- Standart library imports
import ftrack_api,logging,shutil
from pathlib import Path
import pprint

#--- data imports

import data
from data import global_variables


#--- --- --- ---#

#logging.getLogger().setLevel(logging.DEBUG)


#--- --- Ftrack variables
api_key = 'YWUwZGY2MGEtYjA4NS00NzcyLThjYzItNTk4NTJkODQ5MWNiOjo2YjZkNjA0Ni00NDZmLTQ4YTctODU3Yy0zNzQ2MDc0M2FmNTk'

types_list = ['production','R&d','Compositing','rendering','storyboard','lookdev','scenario','grading','setDressing','reference','rigging','editing','animation','Lighting','PAO','design','Generic','layout','CFX','FX','modeling']
status_ftrack_list = 'WIP','Not started','-','INV','R&D','RETAKE','Pending Review','REVIEW_team','REVIEW_sup','TO_RENDER','ON HOLD','BUG','APPROVED','DONE','OUT'


class Ftrack_tab(QWidget):
    '''
    Widget containing all the tabs
    '''
    def __init__(self):
        super().__init__()


        self.ftrack_tab_layout = QVBoxLayout()
        self.setLayout(self.ftrack_tab_layout)


        self.ftrack_tab_widget = QTabWidget()
        self.ftrack_tab_widget.setDocumentMode(True)
        self.ftrack_tab_widget.setMovable(True) 
        self.ftrack_tab_layout.addWidget(self.ftrack_tab_widget)

        #self.Main_subtab = Main_subtab()
        #self.ftrack_tab_widget.addTab(self.Main_subtab,'Main')

        self.Assets_subtab = Assets_subtab()
        self.ftrack_tab_widget.addTab(self.Assets_subtab,'Assets')

        #self.Sequences_subtab = Sequences_subtab()
        #self.ftrack_tab_widget.addTab(self.Sequences_subtab,'Sequences')


class Main_subtab(QWidget):
    '''
    Main tab WIP
    '''
    def __init__(self):
        super().__init__()

        self.main_tab_layout = QVBoxLayout()
        self.setLayout(self.main_tab_layout)

        self.synchronize_ftrack_pipeline_button = QPushButton(text='Synchronize Ftrack -> Pipeline')
        self.synchronize_ftrack_pipeline_button.clicked.connect(self.synchronize_ftrack_pipeline)
        self.main_tab_layout.addWidget(self.synchronize_ftrack_pipeline_button )

        self.synchronize_pipeline_ftrack_button = QPushButton(text='Synchronize Pipeline -> Ftrack')
        self.synchronize_pipeline_ftrack_button.clicked.connect(self.synchronize_pipeline_ftrack)
        self.main_tab_layout.addWidget(self.synchronize_pipeline_ftrack_button )

        #pipeline types: characters,item,prop,set
        #ftrack types: chars,item,prop,set

    def synchronize_ftrack_pipeline(self):
        session =   open_ftrack_session()
        

        ftrack_types = 'chars','item','prop','set'
        pipeline_types = 'character','item','prop','set'


        data_dict =  {}

        for pipeline_type in pipeline_types:
            data_dict[pipeline_type] = {}
            data_dict[pipeline_type]['ftrack'] = []
            data_dict[pipeline_type]['pipeline'] = []

            parent_family = session.query(f'''Family where name is {pipeline_type}
                                    and parent.name is 05_asset
                                    and project.name is {global_variables.project_name}''').one()
            assets = session.query(f'''Asset_ where parent.id is {parent_family['id']}''').all()
            
            for asset in assets:
                data_dict[pipeline_type]['ftrack'].append(asset['name'])
            
            #--- --- --- --- ---

            folder_path = Path(global_variables.pipeline_path + '\\' + pipeline_type)

            for asset in folder_path.iterdir():
                data_dict[pipeline_type]['pipeline'].append(str(asset).split('\\')[-1])

            #--- --- --- ---
            #Compare the lists
            #compare the two lists
            #keep what is in ftrack ->
            #print(set(ftrack).difference(pipeline))


        pprint.pprint(data_dict)

        session.close()


    def synchronize_pipeline_ftrack(self):
        pass


class Assets_subtab(QWidget):
    '''
    Tab with all the subtabs characters,items,sets and props
    '''
    def __init__(self):
        super().__init__()

        self.tab_layout = QVBoxLayout()
        self.setLayout(self.tab_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setMovable(True) 
        self.tab_widget.setDocumentMode(True)
        self.tab_layout.addWidget(self.tab_widget)


        self.characters_tab =Asset_type_subsubtab(asset_type='chars')
        self.tab_widget.addTab(self.characters_tab,'character tab')

        self.items_tab = Asset_type_subsubtab(asset_type='item')
        self.tab_widget.addTab(self.items_tab,'item tab')

        self.sets_tab = Asset_type_subsubtab(asset_type='set')
        self.tab_widget.addTab(self.sets_tab,'set tab')

        self.props_tab = Asset_type_subsubtab(asset_type='prop')
        self.tab_widget.addTab(self.props_tab,'prop tab')

        
class Asset_type_subsubtab(QWidget):

    '''
    Create a Treeview with a custom TreeModel to get the data from ftrack 
    and Comboboxes to change the data in ftrack
    work with an asset typ(prop,item,chars or set)
    '''

    def __init__(self,asset_type:str):
        super().__init__()

        self.asset_type = asset_type
        self.subtab_layout = QVBoxLayout()
        self.setLayout(self.subtab_layout)

        self.model = TreeModel(asset_type=self.asset_type)
    
        self.treeview_wgt = Treeview_SubClass(model=self.model)
        self.treeview_wgt.setModel(self.model)
        self.subtab_layout.addWidget(self.treeview_wgt)

        #--- --- ---

        props_status_delegate = ComboBoxDelegate(model=self.model,data_type ='status' ,itemlist=status_ftrack_list)
        self.treeview_wgt.setItemDelegateForColumn(2, props_status_delegate)

        props_assignee_delegate = ComboBoxDelegate(model=self.model,data_type='assignee',itemlist=global_variables.project_users)
        self.treeview_wgt.setItemDelegateForColumn(4, props_assignee_delegate)

        #--- --- ---

        asset_group = QGroupBox("Asset Creation")
        asset_layout = QGridLayout()
        asset_group.setLayout(asset_layout)
        
        self.create_asset_button = QPushButton(text="Create Asset")
        self.create_asset_button.clicked.connect(self.create_asset_global)
        self.create_folders_pipe = QCheckBox(text="Create directories on pipeline")
        self.create_folders_pipe.setChecked(True)
        self.query_asset_name = QLineEdit()

        asset_layout.addWidget(QLabel("Asset name:"), 0, 0)
        asset_layout.addWidget(self.query_asset_name,0,1)
        asset_layout.addWidget(self.create_folders_pipe, 1, 0)
        asset_layout.addWidget(self.create_asset_button, 1, 1)


        self.subtab_layout.addWidget(asset_group)

        #--- --- ---

        task_group = QGroupBox("Task Creation")
        task_layout = QGridLayout()
        task_group.setLayout(task_layout)

        self.current_parent_asset = QLabel()
        self.set_current_asset_selection()
        self.treeview_wgt.clicked.connect(self.set_current_asset_selection)
        self.query_task_name = QLineEdit()
        self.query_task_type= QComboBox()
        self.query_task_type.addItems(types_list)
        self.create_task_button = QPushButton(text="Create Task")
        self.create_task_button.clicked.connect(self.create_task_global)

        task_layout.addWidget(QLabel("Task Name:"), 0, 0)
        task_layout.addWidget(self.query_task_name, 0, 1)
        task_layout.addWidget(QLabel('Task type:'),0,2)
        task_layout.addWidget(self.query_task_type,0,3)
        task_layout.addWidget(QLabel('Current parent asset:'),1,0)
        task_layout.addWidget(self.current_parent_asset,1,1)

        task_layout.addWidget(self.create_task_button, 3,0)

        self.subtab_layout.addWidget(task_group)
        

        #--- --- ---
        utilities_group = QGroupBox('Utilities')
        utilities_layout = QGridLayout()
        utilities_group.setLayout(utilities_layout)

        self.reset_treeview_button = QPushButton(text='Reset treeview')
        self.reset_treeview_button.clicked.connect(self.reset_treeview)
        self.delete_selection_button = QPushButton(text='Delete selection')
        self.delete_selection_button.clicked.connect(self.delete_selection)

        utilities_layout.addWidget(self.reset_treeview_button,0,0)
        utilities_layout.addWidget(self.delete_selection_button,0,1)

        self.subtab_layout.addWidget(utilities_group)

    def create_folder_asset(self):

        asset_type = self.asset_type
        if asset_type == 'chars':
            asset_type = 'character'

        asset_name = self.query_asset_name.text()

        shutil.copytree(src=global_variables.pipeline_path+'\\04_asset\\template\\_template_workspace_asset',dst=global_variables.pipeline_path+'\\04_asset'+ '\\' + asset_type + '\\' + asset_name)


    def create_asset_global(self):
        '''
        create an asset , basic children tasks and refresh the model, calls create_task func
        '''
        asset_type = self.asset_type
        asset_name = self.query_asset_name.text()

        session = open_ftrack_session()
        asset = create_asset_ftrack(manage_connection=False,asset_name=asset_name,asset_type=asset_type,session=session)
        session.commit()

       
        create_task(manage_connection=False,task_name=asset['name']+'_modeling',task_type='modeling',parent=asset['name'],session=session)
        create_task(manage_connection=False,task_name=asset['name']+'_dressing',task_type='modeling',parent=asset['name'],session=session)
        create_task(manage_connection=False,task_name=asset['name']+'_rig',task_type='rig',parent=asset['name'],session=session)
        create_task(manage_connection=False,task_name=asset['name']+'_lookdev',task_type='lookdev',parent=asset['name'],session=session)
        create_task(manage_connection=False,task_name=asset['name']+'_texturing',task_type='lookdev',parent=asset['name'],session=session)
        create_task(manage_connection=False,task_name=asset['name']+'_uv',task_type='lookdev',parent=asset['name'],session=session)


        session.commit()
        session.close()


        self.create_folder_asset()

        self.reset_treeview()


    def reset_treeview(self):
        '''
        deletes the model of the treeview, relaunch it and set it back
        '''
        self.treeview_wgt.setModel(None)
        self.model = TreeModel(asset_type=self.asset_type)
        self.treeview_wgt.setModel(self.model)


    def create_task_global(self):
        '''
        create a task and refresh the model, calls create_task func
        '''
        task_type = self.query_task_type.currentText()
        task_name = self.query_task_name.text()
        parent = self.current_parent_asset.text()
        session = open_ftrack_session()
        task = create_task(manage_connection=False,task_name=task_name,task_type=task_type,parent=parent,session=session)
        session.commit()

        parent_index = self.treeview_wgt.selectionModel().currentIndex()
        self.model.add_child(parent_index = parent_index,task=task)
        
        session.close()


    def get_assets(self,type:str,manage_connection:bool,session)-> dict:
        '''
        returns a dict with the assets and their data of the chosen type(set,item,character or prop)
        '''
        if manage_connection is True:
            session = open_ftrack_session()

        assets = session.query(f'''Asset_ where parent.name is {type} and project.name is {global_variables.project_name} ''').all()
        
        assets_dict = {}

        for asset in assets:
            assets_dict[asset.name] = {}

        if manage_connection is True:
            session.close()
    

    def set_current_asset_selection(self):
        logging.debug('Executing set_current_asset_selection')
        self.current_parent_asset.clear()
        index = self.treeview_wgt.selectionModel().currentIndex()
        
        if index.isValid():
            item = index.internalPointer()

            if not item.type == self.asset_type:
                parent_item = item.parent_item
                current_selection = parent_item.name_item

            else :
                current_selection = item.name_item
            
        else:
            current_selection = 'Nothing is selected'

        self.current_parent_asset.setText(current_selection)


    def delete_selection(self):
        index = self.treeview_wgt.selectionModel().currentIndex()
        
        if index.isValid():
            item = index.internalPointer()


        msg_box = QMessageBox()
        msg_box.setWindowTitle('Delete ??? Really ???')
        msg_box.setText(f'Are you sure you want to delete the item {item.name_item} ?')
        msg_box.setIcon(QMessageBox.Warning)

        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        result = msg_box.exec()

        if result == QMessageBox.Yes:

            selection_id = item.ftrack_id
            session=open_ftrack_session()
            entity = session.get('TypedContext', selection_id)
            session.delete(entity=entity)
            session.commit()
            session.close()

            parent_item  = item.parent_item
            self.model.beginRemoveRows(index.parent(), index.row(), index.row())
            parent_item.children_items.remove(item)
            self.model.endRemoveRows()
        else:
            return   


class Sequences_subtab(QWidget):
    '''
    still empty
    '''
    def __init__(self,):
        super().__init__()


def open_ftrack_session():
    '''
     opens ftrack session
    '''
    session = ftrack_api.Session(
    server_url=global_variables.server_url,
    api_key=api_key,
    api_user=global_variables.api_user,)

    return session


class Treeview_SubClass(QTreeView):
    '''
    basic Treeview with a given model and some animations
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


class TreeItem:

    '''
    Tree item for the ftrack treeview
    contains name_item,type,status,end_date,assignee, children and parent
    '''

    def __init__(self,item_data, parent=None):
        #We get the name, path,type,size,modification_date,creation_date,parent and children. self.is_loaded checks if the item already has been loaded in the treeview
        logging.debug('creating instance of TreeItem')

        self.name_item = item_data['name']
        self.type = item_data['type']
        self.status = item_data['status']
        self.end_date= item_data['end_date']
        self.assignee = item_data['assignee']
        self.ftrack_id = item_data['ftrack_id']

        self.children_items = []

        self.parent_item = parent
        
        self.is_loaded = False  

    def append_child(self, child):
        logging.debug('Launching append_child')
        self.children_items.append(child)

    def child(self, row):
        logging.debug('Launching child')
        return self.children_items[row]

    def row(self):
        logging.debug('Launching parent')
        if self.parent_item:
            return self.parent_item.children_items.index(self)
        return 0


def change_ftrack_data(task_name,parent_name,data_type,data):
    '''
    changes the status or assignee for the given ftrack element
    '''
    logging.debug('launching change_ftrack_data')
    
    session = open_ftrack_session()
    
    task = session.query(f'''Task where  project.name is {global_variables.project_name}
                         and parent.name is {parent_name}
                         and name is {task_name}
                         
                         ''').first()

    if data_type == 'status':

        task['status']['name'] = data

    if data_type == 'assignee':
        new_assignee = session.query(f'User where last_name is "{data}"').first()


        assignments = list(task['assignments'])
        if assignments:
            for assignment in assignments:
                session.delete(assignment)

        session.create('Appointment', {
                'context': task,
                'resource': new_assignee,
                'type': 'assignment'
            })

    session.commit()
    session.close()


class TreeModel(QAbstractItemModel):
    #Custom model for the treeview, bypassing the issues of the remoteva servern
    def __init__(self,asset_type:str,parent=None):
        super(TreeModel, self).__init__(parent)
        logging.debug('Launching treeview_model')

        self.asset_type = asset_type

        placeholder_root_item_dict = {'name':'placeholder_name',
                                      'type':'placeholder_type',
                                    'status':'placeholder_status',
                                    'end_date':'placeholder_end_date',
                                    'assignee':'placeholder_assignee',
                                    'ftrack_id':'placeholder_id'}
        
        self.root_item = TreeItem(item_data=placeholder_root_item_dict)
    
    def change_item_data(self,index,data_type,data):
        if not index.isValid():
            return
        item = index.internalPointer()
        setattr(item, data_type, data)
        change_ftrack_data(task_name=item.name_item,parent_name=item.parent_item.name_item,data_type=data_type,data=data)
        return
    
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        flags = super().flags(index)
        
        if index.column() == 2:
            flags |= Qt.ItemIsEditable
        if index.column() == 4:
            flags |= Qt.ItemIsEditable
        return flags
    
    def data(self, index, role=Qt.DisplayRole):
        logging.debug('launching data')

        if not index.isValid():
            return None
        item = index.internalPointer()
        #name_item,type,status,end_date,assignee
        
        #setting data
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.name_item
            elif index.column() == 1:
                return item.type
            elif index.column() == 2:
                return item.status
            elif index.column() == 3:
                return item.end_date
            elif index.column() == 4:
                return item.assignee

            
        #setting special font
        if role == Qt.FontRole:
            if item.type == "folder":
                bold_font = QFont()
                bold_font.setBold(True)
                return bold_font
            
        #settings colors
        if role == Qt.ForegroundRole :
            if item.type == self.asset_type and index.column() == 0:
                return QColor("white")  
            else:
                return QColor('lightGray')  
            
        #setting icons
        '''if role == Qt.DecorationRole and index.column() == 0:
            if item.type == 'folder':
                icon_path = str(app_folder / 'icons' / 'folder_icon.png')
                return QIcon(icon_path)'''

    def rowCount(self, parent=QModelIndex()):
        logging.debug("Launching rowCount")
        if parent.isValid():
            parent_item = parent.internalPointer()
        else:
            parent_item = self.root_item

        if parent_item.type == self.asset_type and not parent_item.is_loaded:
            return 1 
        
        if parent_item.children_items:
            return len(parent_item.children_items)
            
        else:
            return 0

    def columnCount(self, parent=QModelIndex()):
        logging.debug('Launching columnCount')
        #Return the number of columns for the children of the given parent
        #name_item,type,status,end_date,assignee
        return 5
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        logging.debug('Launching headerData')
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "--- Name ---"
            elif section == 1:
                return "--- Type ---"
            elif section == 2:
                return '--- Status ---'
            elif section == 3:
                return '--- End date ---'
            elif section == 4:
                return '--- Assignee ---'

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
            index = self.createIndex(row, column, child_item)
            return index
        
        return QModelIndex()

    def parent(self, index):
        logging.debug('Launching parent')
        #Return the parent of the item referred to by the given index

        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent_item

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
        if parent_item.type == self.asset_type or parent_item.type == 'placeholder_type':
            return True
        
        else:
            return False
        
        #return parent_item.is_directory() and not parent_item.is_loaded

    def fetchMore(self, parent):
        logging.debug('fetchmore')

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if parent_item.is_loaded:
            return
        parent_item.is_loaded = True

        session = open_ftrack_session()
        
        folder_name = '05_asset'

        if parent_item.type== 'placeholder_type':
            
            family_name = 'character' if self.asset_type == 'chars' else 'item' if self.asset_type == 'item' else 'prop' if self.asset_type == 'prop' else 'set' if self.asset_type == 'set' else None
            
            assets = session.query(f'''Asset_ where project.name is {global_variables.project_name}
                                   and parent.parent.name is {folder_name}
                                    and  parent.name is {family_name}
                                    ''').all()
            #name,type,end_date,status,assignee
            data_dict = {}
            for asset in assets:
                data_dict[asset['name']] = {'name':asset['name'],
                                            'type':asset['type']['name'],
                                            'end_date':None,
                                            'status':None,
                                            'assignee':None,
                                            'ftrack_id':asset['id']}
            
            
        if parent_item.type == self.asset_type:

            tasks = session.query(f'''Task where project.name is {global_variables.project_name}
                                    and  parent.id is {parent_item.ftrack_id}''').all()
            data_dict = {}
            for task in tasks:

                for assignment in task['assignments']:
                    assignee = assignment['resource']['last_name']
                
                if not  task['assignments']:
                    assignee = '-'

                data_dict[task['name']] = {'name':task['name'],
                                            'type':task['type']['name'],
                                            'end_date':task['end_date'],
                                            'status':task['status']['name'],
                                            'assignee':assignee,
                                            'ftrack_id':task['id']}

        session.close()
        
        for key in data_dict:
            child_item = TreeItem(item_data=data_dict[key], parent=parent_item)
            parent_item.append_child(child_item)

        self.beginInsertRows(parent, 0, len(parent_item.children_items) - 1)
        self.endInsertRows()

    def add_child(self,parent_index,task):

        if not parent_index.isValid():
            return

        parent_item = parent_index.internalPointer()

        data_dict = {}

        data_dict=  {'name':task['name'],
                        'type':task['type']['name'],
                        'end_date':task['end_date'],
                        'status':task['status']['name'],
                        'assignee':'-',
                        'ftrack_id':task['id']}

        position = len(parent_item.children_items)

        new_child = TreeItem(item_data=data_dict,parent=parent_item)

        self.beginInsertRows(parent_index, position, position)


        parent_item.append_child(new_child)


        self.endInsertRows()


class ComboBoxDelegate(QStyledItemDelegate):
    """
    ComboBox view inside of a Table. It only shows the ComboBox when it is
    being edited.
    """

    def __init__(self, model,data_type, itemlist=None):
        
        super().__init__(model)
        self.model = model
        self.itemlist = itemlist or []
        self.data_type = data_type
        # end Constructor

    def createEditor(self, parent, option, index):
        
        if self.itemlist is None:
            self.itemlist = self.model.getItemList(index)

        editor = QComboBox(parent)
        editor.addItems(self.itemlist)
        editor.setCurrentIndex(0)
        editor.installEventFilter(self)
        return editor
    # end createEditor

    def setEditorData(self, editor, index):
        
        value = index.data(Qt.DisplayRole)
        i = editor.findText(value)
        if i == -1:
            i = 0
        editor.setCurrentIndex(i)
    # end setEditorData

    def setModelData(self, editor, model, index):
        
        value = editor.currentText()
        
        model.change_item_data(index=index,data_type=self.data_type,data=value)


def create_asset_ftrack(manage_connection:bool,asset_name:str,asset_type:str,session=None):
    '''
    create an asset in ftrack
    '''

    if manage_connection:
        session = open_ftrack_session()

    #character item prop set

    family_name = 'character' if asset_type == 'chars' else 'item' if asset_type == 'item' else 'prop' if asset_type == 'prop' else 'set' if asset_type == 'set' else None

    parent_family = session.query(f'''Family where name is {family_name}
                                  and parent.name is 05_asset
                                  and project.name is {global_variables.project_name}''').one()
    
    asset_type = session.query(f'Type where name is {asset_type}').one()

    new_asset = session.create('Asset_',{
        'name':asset_name,
        'parent':parent_family,
        'type':asset_type},)
    

    if manage_connection:
        session.commit()
        session.close()
        
    return new_asset

def create_task(manage_connection:bool,task_name:str,task_type:str,parent,session=None):

    if manage_connection:
        session = open_ftrack_session()

    types_list = ['production','R&d','Compositing','rendering','storyboard','lookdev','scenario','grading','setDressing','reference','rigging','editing','animation','Lighting','PAO','design','Generic','layout','CFX','FX','modeling']
    if not task_type in types_list:
        task_type = 'Generic'

    task_type = session.query(f"Type where name is {task_type}").one()

    parent_asset = session.query(f'''Asset_ where project.name is {global_variables.project_name}
                                 and parent.parent.name is 05_asset
                                 and name is {parent}''').first()
    
    task = session.create('Task',{
        'name':task_name+'_task',
        "parent":parent_asset,
        'type': task_type})

    if manage_connection:
        session.commit()
        session.close()

    return task


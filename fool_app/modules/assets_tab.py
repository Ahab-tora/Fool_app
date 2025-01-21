
#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QAbstractItemView,QHBoxLayout,QListView,QWidget,QLineEdit,QVBoxLayout,QPushButton,QTabWidget,QGroupBox,QDialogButtonBox,QDialog,QLabel
from PySide6.QtWidgets import  QGridLayout, QWidget, QVBoxLayout,QPushButton,QLineEdit, QMessageBox
from PySide6.QtGui import QStandardItemModel,QStandardItem,QDrag
from PySide6.QtCore import Qt,QMimeData,QUrl

#--- Standard library imports
import os,shutil,sqlite3,logging
from pathlib import Path
import requests

#--- data imports

import data
from data import global_variables

#--- --- --- ---#

#types are character,item,prop or set


class Assets_tab(QWidget):
    def __init__(self):
        super().__init__()



        self.asset_tab_layout = QVBoxLayout()
        self.setLayout(self.asset_tab_layout)

        self.assets_tab_widget = QTabWidget()
        self.asset_tab_layout.addWidget(self.assets_tab_widget)

        '''self.character_tab = Assets_subtab(table_path=tables_folder+'\\character.db',asset_type='character')
        self.assets_tab_widget.addTab(self.character_tab,'character_tab')

        self.item_tab = Assets_subtab(table_path=tables_folder+'\\item.db',asset_type='item')
        self.assets_tab_widget.addTab(self.item_tab,'item tab')

        self.prop_tab = Assets_subtab(table_path=tables_folder+'\\prop.db',asset_type='prop')
        self.assets_tab_widget.addTab(self.prop_tab,'prop tab')

        self.set_tab = Assets_subtab(table_path=tables_folder+'\\set.db',asset_type='set')
        self.assets_tab_widget.addTab(self.set_tab,'set tab')'''
        
        response = requests.get(f'{global_variables.base_url}/get_assets_types')
        asset_types = response.json()



        #we create Assets_subtab instance for each asset type, example : character,item,prop,FX
        self.Assets_subtab_instances = {}
        for asset_type in asset_types:
            print(asset_type)
            self.Assets_subtab_instances[asset_type] = Assets_subtab(asset_type=asset_type)
            self.assets_tab_widget.addTab(self.Assets_subtab_instances[asset_type],asset_type)



        self.publish_tab = Publish_tab()
        self.assets_tab_widget.addTab(self.publish_tab,'publish tab')


class Publish_tab(QWidget):
    def __init__(self):
        super().__init__()

        self.publish_tab_layout = QVBoxLayout()
        self.setLayout(self.publish_tab_layout)
        self.table_path = global_variables.tables_path + '\\publish.db'
        
        self.list_view_model = QStandardItemModel()

        self.list_view = QListView()
        self.list_view.setModel(self.list_view_model)
        self.publish_tab_layout.addWidget(self.list_view)
        self.list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.refresh_view()


        self.publish_button = QPushButton('publish selection')
        self.publish_button.clicked.connect(self.publish_selection)
        self.publish_tab_layout.addWidget(self.publish_button)

        self.refresh_button = QPushButton('refresh view')
        self.refresh_button.clicked.connect(self.refresh_view)
        self.publish_tab_layout.addWidget(self.refresh_button)

        self.delete_button = QPushButton('delete selection')
        self.delete_button.clicked.connect(self.delete_selection)
        self.publish_tab_layout.addWidget(self.delete_button)

    def publish_selection(self):
        dialog = QDialog()
        dialog.setWindowTitle('New file name')

        #dialog.setWindowIcon(QDialog.Question)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        label = QLabel('Please write down the name of the publish:')
        layout.addWidget(label)

        name_query_edit = QLineEdit()
        layout.addWidget(name_query_edit)

        OK_button = QPushButton('OK')
        layout.addWidget(OK_button)
        OK_button.clicked.connect(dialog.accept)

        Cancel_button = QPushButton('Cancel')
        layout.addWidget(Cancel_button)
        Cancel_button.clicked.connect(dialog.reject)

        #dialog.setWindowIcon(QDialog.question)
       
        if dialog.exec() == 1:
            new_name = name_query_edit.text()

            index = self.list_view.currentIndex()
            item = self.list_view_model.itemFromIndex(index)
            name = item.text()

            #--- --- ---

            response = requests.get(f'{global_variables.base_url}/refresh_publish_view')
            file_path = response.json()
            extension = file_path.split('.')[-1]

            #--- --- ---

            requests.delete(f'{global_variables.base_url}/delete_selection_from_publish/{name}')

            #--- --- ---

            destination_path = file_path.replace(name,new_name).replace('edit','publish') + '.' + extension

            shutil.copy(src=file_path,dst=destination_path)

        else:
            return
    

    def refresh_view(self):
        '''
        we query the names of all the assets in the publish table and populate the model 
        with the assets ready to be reviewed and then published
        '''

        self.list_view_model.clear()

        #--- --- ---
        response = requests.get(f'{global_variables.base_url}/refresh_publish_view')
        results = response.json()

        #--- --- ---

        for element in results:
            item = QStandardItem(element[0])
            self.list_view_model.appendRow(item)


    def delete_selection(self):
        '''
        deletes an item from the publish database
        '''

        index = self.list_view.currentIndex()
        item = self.list_view_model.itemFromIndex(index)
        selection = item.text()
        requests.delete(f'{global_variables.base_url}/delete_selection_from_publish/{selection}')


class Assets_subtab(QWidget):

    def __init__(self,asset_type):
        super().__init__()
        print('constructor for assests_subtab launched')
        self.asset_type = asset_type

        self.Assets_subtab_layout = QHBoxLayout()
        self.setLayout(self.Assets_subtab_layout)


        self.listview_layout = QVBoxLayout()
        self.departments_tab_layout = QHBoxLayout()

        self.Assets_subtab_layout.addLayout(self.listview_layout)
        self.Assets_subtab_layout.addLayout(self.departments_tab_layout)
        self.Assets_subtab_layout.setStretch(0, 3.5) 
        self.Assets_subtab_layout.setStretch(1, 6.5)


        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.update_list_view)
        self.listview_layout.addWidget(self.search_box)

        self.assets_list_view = QListView()
        self.assets_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listview_layout.addWidget(self.assets_list_view)
        self.asset_selection = ''
        self.assets_list_view.clicked.connect(self.set_asset_selection)
        self.assets_list_view.doubleClicked.connect(self.open_asset_folder)

        self.create_folder_asset_button = QPushButton('create new asset')
        self.create_folder_asset_button.clicked.connect(self.create_folder_asset)
        self.listview_layout.addWidget(self.create_folder_asset_button)

        self.model = QStandardItemModel()
        self.assets_list_view.setModel(self.model)
        self.set_list_view_assets()

        self.asset_subtab_tab_widget = QTabWidget()
        self.departments_tab_layout.addWidget(self.asset_subtab_tab_widget)

        self.Maya_subtab = Maya_subtab(asset_type=self.asset_type,Assets_subtab = self)
        self.asset_subtab_tab_widget.addTab(self.Maya_subtab,'Maya')

        self.Houdini_subtab = Houdini_subtab(asset_type=self.asset_type,Assets_subtab = self)
        self.asset_subtab_tab_widget.addTab(self.Houdini_subtab,'Houdini')

    def create_folder_asset(self):
        dialog = QDialog()
        dialog.setWindowTitle('New asset name')

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        label = QLabel('Please write down the name of the new asset:')
        layout.addWidget(label)

        name_query_edit = QLineEdit()
        layout.addWidget(name_query_edit)

        OK_button = QPushButton('OK')
        layout.addWidget(OK_button)
        OK_button.clicked.connect(dialog.accept)

        Cancel_button = QPushButton('Cancel')
        layout.addWidget(Cancel_button)
        Cancel_button.clicked.connect(dialog.reject)


        if dialog.exec() == 1:
            asset_name = name_query_edit.text()
            shutil.copytree(src=global_variables.pipeline_path+'\\04_asset\\template\\_template_workspace_asset',dst=global_variables.pipeline_path+'\\04_asset'+ '\\' + self.asset_type + '\\' + asset_name)
            self.update_list_view()
        else:
            return
        
    
    def open_asset_folder(self):
        os.startfile(global_variables.pipeline_path + '\\04_asset' + '\\' + self.asset_type + '\\'  +self.asset_selection)

    def set_asset_selection(self):
        
        index = self.assets_list_view.currentIndex()
        item = self.model.itemFromIndex(index)
        self.asset_selection = item.text()
        
    def update_list_view(self):
        
        search = self.search_box.text()

        self.model.clear()

        if not search:
            self.set_list_view_assets()
            return

        response = requests.get(f'{global_variables.base_url}/get_assets_from_search/{self.asset_type}/{search}')
        results = response.json()

        for element in results:
            item = QStandardItem(element[0])
            self.model.appendRow(item)

    def set_list_view_assets(self):

        self.model.clear()

        response = requests.get(f'{global_variables.base_url}/get_assets/{self.asset_type}')
        results = response.json()

        for element in results:
            item = QStandardItem(element[0])
            self.model.appendRow(item)


class Maya_subtab(QWidget):
    def __init__(self,asset_type,Assets_subtab):
        super().__init__()
        self.asset_type = asset_type
        self.Assets_subtab = Assets_subtab

        self.Maya_subtab_layout = QHBoxLayout()
        self.setLayout(self.Maya_subtab_layout)

        self.Maya_subtab_tab_widget = QTabWidget()
        self.Maya_subtab_layout.addWidget(self.Maya_subtab_tab_widget)

        departments_list = 'assetLayout','cloth','dressing','groom','lookdev','modeling','rig','sculpt'
        self.departments_tabs = {}

        for department in departments_list:
            
            self.departments_tabs[department] = Maya_department_subtab(department=department,asset_type=self.asset_type,asset_subtab = self.Assets_subtab )
            self.Maya_subtab_tab_widget.addTab(self.departments_tabs[department],department)


class Houdini_subtab(QWidget):
    
    def __init__(self,asset_type,Assets_subtab):
        super().__init__()
        self.asset_type = asset_type
        self.Assets_subtab = Assets_subtab

        self.Houdini_subtab_layout = QHBoxLayout()
        self.setLayout(self.Houdini_subtab_layout)

        self.Houdini_subtab_tab_widget = QTabWidget()
        self.Houdini_subtab_layout.addWidget(self.Houdini_subtab_tab_widget)

        
        departments_list = 'abc','audio','comp','desk','flip','geo','hdz','render','scripts','sim','tex','video'
        self.departments_tabs = {}

        for department in departments_list:
            
            self.departments_tabs[department] = Houdini_department_subtab(department=department,asset_type=self.asset_type,asset_subtab = self.Assets_subtab)
            self.Houdini_subtab_tab_widget.addTab(self.departments_tabs[department],department)


class Houdini_department_subtab(QWidget):
    '''
    
    '''
    def __init__(self,department,asset_type,asset_subtab):
        super().__init__()

        self.department = department
        self.asset_type = asset_type
        self.asset_subtab = asset_subtab

        self.Houdini_department_subtab_layout = QVBoxLayout()
        self.setLayout(self.Houdini_department_subtab_layout)

        self.status_tab = Status_subtab(status='None',asset_type=self.asset_type,department=self.department,asset_subtab=self.asset_subtab,software='houdini',parent=self)
        self.Houdini_department_subtab_layout.addWidget(self.status_tab)


    def open_asset_department_folder(self):
        print('uh')
        #os.startfile(pipeline_path + '\\04_asset' + '\\' + self.asset_type + '\\'  +self.asset_selection)


class Maya_department_subtab(QWidget):
    '''
    
    '''
    def __init__(self,department,asset_type,asset_subtab):
        super().__init__()

        self.department = department
        self.asset_type = asset_type
        self.asset_subtab = asset_subtab

        self.Maya_department_subtab_layout = QVBoxLayout()
        self.setLayout(self.Maya_department_subtab_layout)

        self.Maya_department_subtab_tab_widget = QTabWidget()
        self.Maya_department_subtab_layout.addWidget(self.Maya_department_subtab_tab_widget)
        #self.Maya_department_subtab_tab_widget.mouseDoubleClickEvent.connect(self.open_asset_department_folder)


        self.edit_tab = Status_subtab(status='edit',asset_type=self.asset_type,department=self.department,asset_subtab=self.asset_subtab,software='maya',parent=self)
        self.Maya_department_subtab_tab_widget.addTab(self.edit_tab,'edit')

        self.publish_tab = Status_subtab(status='publish',asset_type=self.asset_type,department=self.department,asset_subtab=self.asset_subtab,software='maya',parent=self)
        self.Maya_department_subtab_tab_widget.addTab(self.publish_tab,'publish')

    def open_asset_department_folder(self):
        print('uh')
        #os.startfile(pipeline_path + '\\04_asset' + '\\' + self.asset_type + '\\'  +self.asset_selection)


class Status_subtab(QWidget):
    def __init__(self,status:str,asset_type:str,department:str,asset_subtab,software,parent):
        super().__init__()
        
        #--- --- Variables
        self.status = status
        self.software = software
        self.asset_type = asset_type
        self.department = department
        self.asset_subtab = asset_subtab

        self.setAcceptDrops(True)
        
        #self.table_path = table_path

        #--- --- Layout
        self.status_layout = QVBoxLayout()
        self.setLayout(self.status_layout)

        #--- --- Search box
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.set_model_data_from_search)
        self.status_layout.addWidget(self.search_box)
        
        #--- --- files list_view
        self.files_list_view = QListView()
        self.files_list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.status_layout.addWidget(self.files_list_view)
        
        #--- ---  Item model
        self.model = QStandardItemModel()
        
        self.asset_subtab.assets_list_view.clicked.connect(self.set_model_data)
        self.asset_subtab.asset_subtab_tab_widget.currentChanged.connect(self.set_model_data)
        #parent.Maya_department_subtab_tab_widget.currentChanged.connect(self.set_model_data)

        self.files_list_view.doubleClicked.connect(self.open_file)
        
        self.files_list_view.setModel(self.model)

        #--- --- ---

        self.buttons_group= QGroupBox()
        self.buttons_layout= QGridLayout()
        self.buttons_group.setLayout(self.buttons_layout)
        self.status_layout.addWidget(self.buttons_group)

        #--- --- ---

        self.drop_as_reference_button = Drop_reference_button(text='Drop reference in maya',parent=self)
        self.buttons_layout.addWidget(self.drop_as_reference_button,1,0)

        if 'maya' == self.software:
            self.drop_set_project_button = QPushButton('Drop set project')
            self.buttons_layout.addWidget(self.drop_set_project_button,1,1)

            self.set_for_review_button = QPushButton('Set for review')
            self.set_for_review_button.clicked.connect(self.set_for_review)
            self.buttons_layout.addWidget(self.set_for_review_button ,1,2)

        #--- --- ---

        softwares  =('maya','.ma'),('houdini','.hipnc'),('nuke','.nk')
        self.set_software_scene_button = {}
        for i,software in enumerate(softwares):
            self.set_software_scene_button[software[0]] = QPushButton(f'Create {software[0]} scene')
            self.buttons_layout.addWidget(self.set_software_scene_button[software[0]] ,0,i)
            self.set_software_scene_button[software[0]].clicked.connect(lambda checked, s=software[0], e=software[1]: self.create_software_file(s, e))

        #nuke,houdini,mari

    def create_software_file(self,software,extension):

        dialog = QDialog()
        dialog.setWindowTitle('New file name')

        #dialog.setWindowIcon(QDialog.Question)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        label = QLabel('Please write down the name of the new file:')
        layout.addWidget(label)

        name_query_edit = QLineEdit()
        layout.addWidget(name_query_edit)

        OK_button = QPushButton('OK')
        layout.addWidget(OK_button)
        OK_button.clicked.connect(dialog.accept)

        Cancel_button = QPushButton('Cancel')
        layout.addWidget(Cancel_button)
        Cancel_button.clicked.connect(dialog.reject)

        asset_name = self.asset_subtab.asset_selection

        response = requests.get(f'{global_variables.base_url}/get_assets_path')
        assets_path  = response.json()

        if dialog.exec() == 1:

            new_file_name = name_query_edit.text()
            if not new_file_name:
                return
            
            if self.software == 'houdini':

                new_file_path = assets_path + '\\' + self.asset_type + '\\' +  asset_name + '\\' +  self.software + '\\' +  self.department + '\\' + new_file_name + extension


            if self.software == 'maya':
                new_file_path = assets_path + '\\' + self.asset_type + '\\' +  asset_name + '\\' +  self.software +'\\scenes' + '\\' +  self.status + '\\' + self.department + '\\' + new_file_name + extension

            file = open(new_file_path, 'a')
            file.close()
            self.set_model_data()
        else:
            return
            

    def dragEnterEvent(self, e):
        e.accept()


    def set_for_review(self):

        table_path = global_variables.tables_path  +'\\'+ self.asset_type+'.db'

        index = self.files_list_view.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        requests.post(f'{global_variables.base_url}/set_for_review/{self.asset_type}/{file}')
        

    def set_model_data(self):
        '''
        set the model data for the given asset_type, asset_name,derpartment and status
        '''

        asset_name = self.asset_subtab.asset_selection
        if not asset_name:
            return
        self.model.clear()

        response = requests.get(f'{global_variables.base_url}/get_files_of_asset/{self.asset_type}/{asset_name}/{self.department}/{self.status}')
        results = response.json()

        x = 0

        for element in results:
            
            item = QStandardItem(element[0])
                
            self.model.appendRow(item)

            if x == 0:
                x+=1
                item = QStandardItem('--- --- --- ---')
                self.model.appendRow(item)


    def open_file(self):
        '''
        opens a file when double clicked
        '''
        index = self.files_list_view.currentIndex()
        item = self.model.itemFromIndex(index)
        file = item.text()

        response = requests.get(f'{global_variables.base_url}/get_path_of_file/{self.asset_type}/{file}')
        results = response.json()

        os.startfile(results)


    def set_model_data_from_search(self):
        '''
        set the model data for the given asset_type, asset_name,derpartment , status AND SEARCH
        '''

        self.model.clear()
        search = f"%{self.search_box.text()}%"

    
        asset_name = self.asset_subtab.asset_selection
        response = requests.get(f'{global_variables.base_url}/get_files_of_asset_search/{self.asset_type}/{asset_name}/{self.department}/{self.status}/{search}')
        results = response.json()

        if not results:
            item = QStandardItem("Nothing here :(")
            self.model.appendRow(item)

        else:
            x = 0
            for element in results:
                print(element)
                item = QStandardItem(element[0])
                print(item)
                self.model.appendRow(item)

                if x == 0:
                    x+=1
                    item = QStandardItem('--- --- --- ---')
                    self.model.appendRow(item)


class Drop_reference_button(QPushButton):
    '''
    A QPushButton allowing to drop references in a maya scene
    '''
    def __init__(self,text,parent):
        super().__init__()

        self.parent= parent
        self.setText(text)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:


            drag = QDrag(self)
            mime = QMimeData()

            #--- --- ---
            index = self.parent.files_list_view.currentIndex()
            item = self.parent.model.itemFromIndex(index)
            file = item.text()
            print(file)
            #--- --- ---
            if not file:
                return


            #--- --- ---

            response = requests.get(f'{global_variables.base_url}/get_file_path_for_reference_drop/{self.parent.asset_type}/{file}')
            file_path = response.json()

            file_path_formatted = file_path.replace('\\','//').replace('//','/')
            print(file_path_formatted)


            maya_code = f'''
import maya.cmds as cmds

def onMayaDroppedPythonFile(*args):
    print('putain')
    

    cmds.file({file_path_formatted}, reference=True)
print('putain x2')


'''

            temp_file_name = 'temp_file_drop.py'
            temp_file_path = global_variables.fool_path + '\\temp\\' + temp_file_name 
            temp_file_path = temp_file_path.replace('\\','/')


            with open(temp_file_path, "w") as temp_file:
                temp_file.write(maya_code)


            mime.setUrls([QUrl.fromLocalFile(temp_file_path)])
            drag.setMimeData(mime)
            drag.exec()

            file_path = Path(temp_file_path)
            file_path.unlink()


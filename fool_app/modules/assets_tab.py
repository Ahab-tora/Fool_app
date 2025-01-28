
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


class Assets_tab(QWidget):
    def __init__(self):
        super().__init__()



        self.asset_tab_layout = QHBoxLayout()
        self.setLayout(self.asset_tab_layout)

        self.assets_tab_widget = QTabWidget()
        self.asset_tab_layout.addWidget(self.assets_tab_widget)
        self.assets_tab_widget.currentChanged.connect(self.asset_subtab_changed)
        self.asset_tab_sublayout = QVBoxLayout()
        self.asset_tab_layout.addLayout(self.asset_tab_sublayout)



        response = requests.get(f'{global_variables.base_url}/get_assets_types')
        asset_types = response.json()


        #we create Assets_subtab instance for each asset type, example : character,item,prop,FX
        self.Assets_subtab_instances = {}
        for asset_type in asset_types:
            print(asset_type)
            self.Assets_subtab_instances[asset_type] = Assets_subtab(asset_type=asset_type,parent_class=self)
            self.assets_tab_widget.addTab(self.Assets_subtab_instances[asset_type],asset_type)
        self.active_asset_subtab = self.assets_tab_widget.currentWidget()


        '''self.publish_tab = Publish_tab()
        self.assets_tab_widget.addTab(self.publish_tab,'publish tab')'''


        #--- --- ---

        self.software_tab_widget = QTabWidget(parent=self)
        self.asset_tab_sublayout.addWidget(self.software_tab_widget,stretch=2)
        self.software_tab_widget.currentChanged.connect(self.software_tab_changed)
        #self.software_tab_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.software_tab_widget.setMaximumHeight(260)

        self.Maya_tab = Maya_tab(parent=self)
        self.software_tab_widget.addTab(self.Maya_tab,'Maya')


        self.Houdini_tab = Houdini_tab(parent=self)
        self.software_tab_widget.addTab(self.Houdini_tab,'Houdini')
        
        self.active_software_tab = self.software_tab_widget.currentWidget()
        
        #--- --- ---

        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.update_listview_from_search)
        self.asset_tab_sublayout.addWidget(self.search_box)

        #--- --- ---
        
        self.files_view_model = QStandardItemModel()
        #self.files_view_model.setHorizontalHeaderLabels(["Name", "Last Modification", "Comment"])
        self.files_view_model.setHorizontalHeaderLabels(["Name", "Last Modification"])

        self.files_view = QTableView()
        self.asset_tab_sublayout.addWidget(self.files_view,stretch=8)
        self.files_view.setModel(self.files_view_model)

        self.files_view.doubleClicked.connect(self.open_file)
        self.files_view.setEditTriggers(QTableView.NoEditTriggers)
        self.files_view.horizontalHeader().setStretchLastSection(True)
        self.files_view.setShowGrid(False)
    
        self.files_view.resizeRowsToContents()  
        self.files_view.resizeColumnsToContents()

        self.files_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.files_view.verticalHeader().hide()
 
        #--- --- ---

        self.buttons_group= QGroupBox()
        self.buttons_layout= QGridLayout()
        self.buttons_group.setLayout(self.buttons_layout)
        self.asset_tab_sublayout.addWidget(self.buttons_group)

        softwares  =('maya','.ma'),('houdini','.hipnc'),('nuke','.nk')

        self.set_software_scene_button = {}
        for i,software in enumerate(softwares):
            print(software)
            self.set_software_scene_button[software[0]] = QPushButton(f'Create {software[0]} scene')
            self.buttons_layout.addWidget(self.set_software_scene_button[software[0]] ,0,i)
            self.set_software_scene_button[software[0]].clicked.connect(lambda checked, s=software[0], e=software[1]: self.create_software_file(s, e))
                
        #--- --- ---

        self.drop_as_reference_button = Drop_reference_button(text='Drop reference in maya',parent=self)
        self.buttons_layout.addWidget(self.drop_as_reference_button,1,0)

        #--- --- ---

        self.publish_selection_button = QPushButton(text='Publish selection')
        self.publish_selection_button.clicked.connect(self.publish_selection)
        self.buttons_layout.addWidget(self.publish_selection_button,1,1)

        #--- --- ---

        self.reset_view_button = QPushButton(text='Reset view')
        self.reset_view_button.clicked.connect(self.update_listview)
        self.buttons_layout.addWidget(self.reset_view_button,1,2)
        

        self.asset_tab_layout.setStretch(0, 3) 
        self.asset_tab_layout.setStretch(1,7)


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


            #--- --- ---

            index = self.files_view.currentIndex()
            item = self.files_view_model.itemFromIndex(index)
            file = item.text()

            asset_type = self.active_asset_subtab.get_asset_type()
            response = requests.get(f'{global_variables.base_url}/get_path_of_file/{asset_type}/{file}')
            file_path= response.json()
            extension = file_path.split('.')[-1]

            
            #--- --- ---
            #get path from name,copy it with new name and extension
            try:
                destination_path = file_path.replace(file,new_name).replace('edit','publish') + '.' + extension
                shutil.copy(src=file_path,dst=destination_path)

            except:
                return

        else:
            return
    

    def open_file(self):
        index = self.files_view.currentIndex()
        item = self.files_view_model.itemFromIndex(index)
        file = item.text()
        asset_type = self.active_asset_subtab.get_asset_type()
        response = requests.get(f'{global_variables.base_url}/get_path_of_file/{asset_type}/{file}')
        results = response.json()

        os.startfile(results)
       

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


        asset_name = self.active_asset_subtab.asset_selection

        response = requests.get(f'{global_variables.base_url}/get_assets_path')
        assets_path  = response.json()

        if dialog.exec() == 1:

            new_file_name = name_query_edit.text()
            if not new_file_name:
                return
            
            asset_type = self.active_asset_subtab.get_asset_type()
            software = self.active_software_tab.software
            department = self.active_software_tab.get_department()
           

            if self.software == 'houdini':

                new_file_path = assets_path + '\\' + asset_type + '\\' +  asset_name + '\\' +  software + '\\' +  department + '\\' + new_file_name + extension


            if self.software == 'maya':
                status = self.active_software_tab.get_status()
                new_file_path = assets_path + '\\' + asset_type + '\\' +  asset_name + '\\' +  software +'\\scenes' + '\\' +  status + '\\' + department + '\\' + new_file_name + extension

            file = open(new_file_path, 'a')
            file.close()

        else:
            return
        

    def asset_subtab_changed(self):
        self.active_asset_subtab = self.assets_tab_widget.currentWidget()
        if not self.active_asset_subtab:
            return
        self.update_listview()

    
    def software_tab_changed(self):
        self.active_software_tab = self.software_tab_widget.currentWidget()
        if not self.active_software_tab:
            return
        self.update_listview()
        print(self.active_software_tab.get_path())
    

    def update_listview_from_search(self):
        self.active_software_tab = self.software_tab_widget.currentWidget()
        if not self.active_software_tab:
            return
        print('--- --- ---')
        print(self.active_software_tab.get_path())
        print(self.active_asset_subtab.get_path())

        asset_type = self.active_asset_subtab.get_asset_type()
        asset_name = self.active_asset_subtab.get_asset_selection()

        department = self.active_software_tab.get_department()
        status = self.active_software_tab.get_status()

        if None in (asset_type, asset_name, department):
            return 
        
        #self.files_view_model.clear()
        self.files_view_model.removeRows(0, self.files_view_model.rowCount())
        search = f"%{self.search_box.text()}%"
        response = requests.get(f'{global_variables.base_url}/get_files_of_asset_search/{asset_type}/{asset_name}/{department}/{status}/{search}')
        results = response.json()

        for result in results:
            name = QStandardItem(result[0])
            last_modification = QStandardItem(result[1].split()[0])
            #comment = QStandardItem(result[2])
            #self.files_view_model.appendRow([name, last_modification, comment])
            self.files_view_model.appendRow([name, last_modification])

        print(results)
        self.files_view.resizeRowsToContents()
        self.files_view.resizeColumnsToContents()
        self.files_view.horizontalHeader().setStretchLastSection(True)


    def update_listview(self):
        self.active_software_tab = self.software_tab_widget.currentWidget()
        if not self.active_software_tab:
            return
        print('--- --- ---')

        print(self.active_software_tab.get_path())
        print(self.active_asset_subtab.get_path())

        asset_type = self.active_asset_subtab.get_asset_type()
        asset_name = self.active_asset_subtab.get_asset_selection()
        
        print(asset_name)
        print(self.active_asset_subtab)

        department = self.active_software_tab.get_department()
        status = self.active_software_tab.get_status()

        if None in (asset_type, asset_name, department):
            return 
        
        #self.files_view_model.clear()
        self.files_view_model.removeRows(0, self.files_view_model.rowCount())

        response = requests.get(f'{global_variables.base_url}/get_files_of_asset/{asset_type}/{asset_name}/{department}/{status}')
        results = response.json()

        for result in results:
            name = QStandardItem(result[0])
            last_modification = QStandardItem(result[1].split()[0])
            #comment = QStandardItem(result[2])
            #self.files_view_model.appendRow([name, last_modification, comment])
            self.files_view_model.appendRow([name, last_modification])

        print(results)
        self.files_view.resizeRowsToContents()
        self.files_view.resizeColumnsToContents()


class Maya_tab(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.parent_class = parent
        self.software = 'Maya'

        self.Maya_subtab_layout = QVBoxLayout()
        self.setLayout(self.Maya_subtab_layout)

        self.setStyleSheet("""
            QRadioButton {
                font-size: 15px;
                font-weight: bold;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 12px;
                border: 2px solid #444;
                border-radius: 10px;
                background: white;
            }
            QRadioButton::indicator:checked {
                background: #0078d7;
                border: 2px solid #0078d7;
            }
        """)

        self.open_software_folder_button = QPushButton('Open maya folder')
        self.open_software_folder_button.clicked.connect(self.open_software)
        self.Maya_subtab_layout.addWidget(self.open_software_folder_button)


        departments_list = 'assetLayout','cloth','dressing','groom','lookdev','modeling','rig','sculpt'

        self.department_button_group = QButtonGroup()
        self.department_button_group.setExclusive(True)
        self.department_buttons_box = QGroupBox()
        self.department_buttons_box_layout = QGridLayout()
        self.department_buttons_box.setLayout(self.department_buttons_box_layout)
        self.Maya_subtab_layout.addWidget(self.department_buttons_box)

        #--- --- ---

        self.departments_buttons = {}
        loop_counter = 0
        grid_row = 0
        for department in departments_list:
            if loop_counter % 8 == 0:
                grid_row += 1
                loop_counter = 0
            self.departments_buttons[department] = QPushButton(department)
            self.departments_buttons[department].setCheckable(True)
            self.departments_buttons[department].setStyleSheet("QPushButton:checked { background-color: #5288B2; }")
            self.department_button_group.addButton(self.departments_buttons[department])                 
            self.department_buttons_box_layout.addWidget(self.departments_buttons[department],grid_row,loop_counter)
            loop_counter += 1
        self.departments_buttons[departments_list[0]].setChecked(True)

        #--- --- ---

        self.open_department_folder_button = QPushButton('Open department folder')
        self.open_department_folder_button.clicked.connect(self.open_department_folder)
        self.Maya_subtab_layout.addWidget(self.open_department_folder_button)

        #--- --- ---

        status_list = 'edit','publish'

        self.status_button_group = QButtonGroup()
        self.status_button_group.setExclusive(True)
        self.status_buttons_box = QGroupBox()
        self.status_buttons_box_layout = QGridLayout()
        self.status_buttons_box.setLayout(self.status_buttons_box_layout)
        self.Maya_subtab_layout.addWidget(self.status_buttons_box)

        self.status_buttons = {}
        loop_counter = 0
        grid_row = 0
        for status in status_list:
            if loop_counter % 4 == 0:
                grid_row += 1
                loop_counter = 0
            self.status_buttons[status] = QPushButton(status)
            self.status_buttons[status].setCheckable(True)
            self.status_buttons[status].setStyleSheet("QPushButton:checked { background-color: #5288B2; }")
            self.status_button_group.addButton(self.status_buttons[status])                 
            self.status_buttons_box_layout.addWidget(self.status_buttons[status],grid_row,loop_counter)
            loop_counter += 1
        self.status_buttons[status_list[0]].setChecked(True)

        self.department_button_group.buttonClicked.connect(self.parent_class.update_listview)
        self.status_button_group.buttonClicked.connect(self.parent_class.update_listview)
    

    def open_software(self):
        software_folder = global_variables.pipeline_path + global_variables.assets_path + '\\' + self.parent_class.active_asset_subtab.get_path() + '\\' + self.software 
        os.startfile(software_folder)
        
    def open_department_folder(self):
        department_folder = global_variables.pipeline_path + global_variables.assets_path + '\\' + self.parent_class.active_asset_subtab.get_path() + '\\' + self.software + '\\scenes \\' + self.get_status() + '\\' + self.get_department()
        os.startfile(department_folder)

    def get_software(self):
        return self.software
    
    def get_status(self):
        status_checked_button = self.status_button_group.checkedButton().text()
        return status_checked_button

    def get_department(self):
        department_checked_button = self.department_button_group.checkedButton().text()
        return department_checked_button

    def get_path(self):
        department_checked_button = self.department_button_group.checkedButton().text()
        status_checked_button = self.status_button_group.checkedButton().text()
        return self.software + '\\scenes\\' + status_checked_button + '\\' + department_checked_button

class Houdini_tab(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.parent_class = parent
        self.software = 'Houdini'

        self.Houdini_subtab_layout = QVBoxLayout()
        self.setLayout(self.Houdini_subtab_layout)

        self.open_software_folder_button = QPushButton('Open houdini folder')
        self.open_software_folder_button.clicked.connect(self.open_software)
        self.Houdini_subtab_layout.addWidget(self.open_software_folder_button)


        departments_list = 'abc','audio','comp','desk','flip','geo','hdz','render','scripts','sim','tex','video'

        self.department_button_group = QButtonGroup()
        self.department_button_group.setExclusive(True)
        self.department_buttons_box = QGroupBox()
        self.department_buttons_box_layout = QGridLayout()
        self.department_buttons_box.setLayout(self.department_buttons_box_layout)
        self.Houdini_subtab_layout.addWidget(self.department_buttons_box)

        self.departments_buttons = {}
        loop_counter = 0
        grid_row = 0
        for department in departments_list:
            if loop_counter % 6 == 0:
                grid_row += 1
                loop_counter = 0
            self.departments_buttons[department] = QPushButton(department)
            self.departments_buttons[department].setCheckable(True)
            self.departments_buttons[department].setStyleSheet("QPushButton:checked { background-color: #5288B2; }")
            self.department_button_group.addButton(self.departments_buttons[department])                 
            self.department_buttons_box_layout.addWidget(self.departments_buttons[department],grid_row,loop_counter)
            loop_counter += 1
        self.departments_buttons[departments_list[0]].setChecked(True)
        
        self.open_department_folder_button = QPushButton('Open department folder')
        self.open_department_folder_button.clicked.connect(self.open_department_folder)
        
        self.Houdini_subtab_layout.addWidget(self.open_department_folder_button)

        self.department_button_group.buttonClicked.connect(self.parent_class.update_listview)
        self.department_button_group.buttonClicked.connect(self.parent_class.update_listview)

    def open_software(self):
        software_folder = global_variables.pipeline_path + global_variables.assets_path + '\\' + self.parent_class.active_asset_subtab.get_path() + '\\' + self.software 
        os.startfile(software_folder)
        
    def open_department_folder(self):
        department_folder = global_variables.pipeline_path + global_variables.assets_path + '\\' + self.parent_class.active_asset_subtab.get_path() + '\\' + self.software + '\\' + self.get_department()
        os.startfile(department_folder)

    def get_software(self):
        return self.software
    
    def get_status(self):
        return None
    
    def get_department(self):
        department_checked_button = self.department_button_group.checkedButton().text()
        return department_checked_button
    
    def get_path(self):
        department_checked_button = self.department_button_group.checkedButton().text()
        return self.software + '\\' + department_checked_button
        



    

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

    def __init__(self,asset_type,parent_class):
        super().__init__()
        print('constructor for assests_subtab launched')
        self.asset_type = asset_type
        self.parent_class = parent_class

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
        self.assets_list_view.clicked.connect(self.parent_class.update_listview)
        
        self.assets_list_view.doubleClicked.connect(self.open_asset_folder)

        self.create_folder_asset_button = QPushButton('create new asset')
        self.create_folder_asset_button.clicked.connect(self.create_folder_asset)
        self.listview_layout.addWidget(self.create_folder_asset_button)

        self.model = QStandardItemModel()
        self.assets_list_view.setModel(self.model)
        self.set_list_view_assets()


    def get_asset_type(self):
        return self.asset_type
    
    def get_asset_selection(self):
        if not self.asset_selection:
            return None
        return self.asset_selection

    def get_path(self):
        if not self.asset_selection:
            return None
        
        return self.asset_type + '\\' + self.asset_selection
    
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

        self.parent_widget= parent
        self.setText(text)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:


            drag = QDrag(self)
            mime = QMimeData()

            #--- --- ---
            index = self.parent_widget.files_view.currentIndex()
            item = self.parent_widget.files_view_model.itemFromIndex(index)
            file = item.text()
            print(file)
            #--- --- ---
            if not file:
                return


            #--- --- ---

            response = requests.get(f'{global_variables.base_url}/get_file_path_for_reference_drop/{self.parent_widget.active_asset_subtab.get_asset_type()}/{file}')
            file_path = response.json()

            file_path_formatted = file_path.replace('\\','//').replace('//','/')
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


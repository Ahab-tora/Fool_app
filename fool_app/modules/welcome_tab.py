#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QWidget,QListWidget,QVBoxLayout,QPushButton,QLabel,QMessageBox,QGroupBox

#---
import ftrack_api,os,json
#---

import data
from data import global_variables

api_key = 'YWUwZGY2MGEtYjA4NS00NzcyLThjYzItNTk4NTJkODQ5MWNiOjo2YjZkNjA0Ni00NDZmLTQ4YTctODU3Yy0zNzQ2MDc0M2FmNTk'


class Welcome(QWidget):
    def __init__(self):
        super().__init__()

        self.loaded = False

        self.welcome_tab_layout = QVBoxLayout()
        self.setLayout(self.welcome_tab_layout)

        self.open_pipeline_button = QPushButton('Open Pipeline')
        self.open_pipeline_button.clicked.connect(self.open_pipeline)
        self.welcome_tab_layout.addWidget(self.open_pipeline_button)

        # --- Recent Files ---
        self.recent_files_group = QGroupBox("Recent Files")
        recent_files_layout = QVBoxLayout()
        
        self.recent_files_QListWidget = QListWidget()
        self.recent_files_QListWidget.itemDoubleClicked.connect(self.open_selected_file)
        self.set_recent_files()
        self.refresh_recent_files = QPushButton("Refresh recent files")
        self.refresh_recent_files.clicked.connect(self.set_recent_files)

        recent_files_layout.addWidget(self.recent_files_QListWidget)
        recent_files_layout.addWidget(self.refresh_recent_files)

        self.recent_files_group.setLayout(recent_files_layout)
        self.welcome_tab_layout.addWidget(self.recent_files_group)

        # --- Favorite Files ---
        self.favorite_files_group = QGroupBox("Favorite Files")
        favorite_files_layout = QVBoxLayout()

        self.favorite_files_QListWidget = QListWidget()
        self.favorite_files_QListWidget.itemDoubleClicked.connect(self.open_selected_file)
        self.set_favorites_files()
        self.refresh_favorite_files = QPushButton("Refresh favorite files")
        self.refresh_favorite_files.clicked.connect(self.set_favorites_files)
        self.delete_favorite_button = QPushButton('Delete favorite')
        self.delete_favorite_button.clicked.connect(self.delete_favorite)

        favorite_files_layout.addWidget(self.favorite_files_QListWidget)
        favorite_files_layout.addWidget(self.refresh_favorite_files)
        favorite_files_layout.addWidget(self.delete_favorite_button)

        self.favorite_files_group.setLayout(favorite_files_layout)
        self.welcome_tab_layout.addWidget(self.favorite_files_group)

        # --- Assigned Tasks ---
        self.tasks_group = QGroupBox("Assigned Tasks")
        tasks_layout = QVBoxLayout()

        self.due_tasks_QListWidget = QListWidget()
        self.refresh_due_tasks = QPushButton("Refresh tasks")
        self.refresh_due_tasks.clicked.connect(lambda: self.set_due_tasks(manage_connection=True))

        tasks_layout.addWidget(self.due_tasks_QListWidget)
        tasks_layout.addWidget(self.refresh_due_tasks)

        self.tasks_group.setLayout(tasks_layout)
        self.welcome_tab_layout.addWidget(self.tasks_group)

        self.set_due_tasks(manage_connection=True)

    def on_display(self):
        self.set_favorites_files()
        self.set_recent_files()

    def open_selected_file(self, item):
        file_path = item.text()
        if os.path.exists(file_path):
            os.startfile(file_path)  # Windows
        else:
            print(f"File not found: {file_path}")
            
    def open_pipeline(self):
        os.startfile(global_variables.pipeline_path)

    def set_due_tasks(self,manage_connection,session=None):
        print('launch set_due_tasks')
        '''
        sets the tasks in the due_tasks_QlistWidget
        '''
        self.due_tasks_QListWidget.clear()
        
        if manage_connection is True:
            session = self.open_ftrack_session()

        due_tasks_dict,sorted_keys = self.query_due_tasks(session=session)

        
        for key in sorted_keys:
            formatted_task_msg = f'''Task: {key} --- for {due_tasks_dict[key]['end_date'].format('DD/MM/YYYY')} --- the status is currently {due_tasks_dict[key]['status']}'''
            self.due_tasks_QListWidget.addItem(formatted_task_msg)

        if manage_connection is True:
            self.close_ftrack_session(session=session)


    def open_ftrack_session(self):
        '''
        opens ftrack session
        '''
        session = ftrack_api.Session(
        server_url=global_variables.server_url,
        api_key=api_key,
        api_user=global_variables.api_user,)
        return session


    def close_ftrack_session(self,session):
        '''
        closes ftrack session
        '''
        session.close()


    def query_due_tasks(self,session):
        '''
        Query all the tasks of the user that are not done and have a due date then adds the data to a dict
        the dict is sorted by due date and contains the name, the due date, and the status of the task
        '''
        user_tasks = session.query(f"Task where assignments.resource.email is '{global_variables.api_user}' and status.name != DONE and end_date != None").all()

        next_due_tasks = {}
        #iterates through the dict and compare the dict[key]['end_date'] to current end_date
        
        #when a date is not superior, append at the index before the current index
        for task in user_tasks:
            next_due_tasks[task['name']] = {'end_date': task['end_date'],'status':task['status']['name']}

        sorted_keys = sorted(next_due_tasks.keys(), key=lambda k: next_due_tasks[k]['end_date'])

        return next_due_tasks,sorted_keys

    def set_favorites_files(self):
        '''
        add the favorite files to the favorite files QlistWidget
        '''
        self.favorite_files_QListWidget.clear()
        try:
            with open(global_variables.fool_path + '\\data\\files_data.json', "r") as file:
                data = json.load(file)
            self.favorite_files_QListWidget.addItems(data["favorites"])
        except:
            QMessageBox.critical(None, "Error", f"Failed to load files_data_json")

    def set_recent_files(self):
        '''
        add the recent files to the recent files QlistWidget
        '''
        self.recent_files_QListWidget.clear()
        try:
            with open(global_variables.fool_path + '\\data\\files_data.json', "r") as file:
                data = json.load(file)
            self.recent_files_QListWidget.addItems(data["recent"])
        except:
            QMessageBox.critical(None, "Error", f"Failed to load files_data_json")
    
    def open_file(self):
        #get path
        #startfile
        pass
    #when opened from treeview or

    def delete_favorite(self):
        to_remove = self.favorite_files_QListWidget.currentItem().text()
        print(to_remove)
        if not to_remove:
            return
        
        try:
            with open(global_variables.fool_path + '\\data\\files_data.json', "r") as file:
                data = json.load(file)

            data["favorites"].remove(to_remove)

            with open(global_variables.fool_path + '\\data\\files_data.json', "w") as file:
                json.dump(data, file, indent=4)
            self.set_favorites_files()
        except:
            self.set_favorites_files()
            QMessageBox.critical(None, "Error", f'error while removing favorite')
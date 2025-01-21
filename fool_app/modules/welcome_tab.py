#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QWidget,QListWidget,QVBoxLayout,QPushButton,QLabel

#---
import ftrack_api

#---

import data
from data import global_variables

api_key = 'YWUwZGY2MGEtYjA4NS00NzcyLThjYzItNTk4NTJkODQ5MWNiOjo2YjZkNjA0Ni00NDZmLTQ4YTctODU3Yy0zNzQ2MDc0M2FmNTk'


def connect_close_ftrack(func):
    def wrapper(*args,**kwargs):

        session = ftrack_api.Session(
        server_url=global_variables.server_url,
        api_key=api_key,
        api_user=global_variables.api_user,)

        executed_function = func(*args,session=session,**kwargs)
        
        session.close()

        return executed_function
    
    return wrapper

class Welcome(QWidget):
    def __init__(self):
        super().__init__()

        self.welcome_tab_layout = QVBoxLayout()
        self.setLayout(self.welcome_tab_layout)

        #self.notes_QTextEdit = QTextEdit()

        self.recent_files_QListWidget = QListWidget()

        self.favorite_files_QListWidget = QListWidget()

        self.due_tasks_QListWidget = QListWidget()

        self.due_task_QLabel = QLabel('Assigned tasks:')

        self.reset_due_tasks = QPushButton('refresh tasks')
        self.reset_due_tasks.clicked.connect(self.set_due_tasks(manage_connection=True))

        #self.welcome_tab_layout.addWidget(self.notes_QTextEdit)
        self.welcome_tab_layout.addWidget(self.recent_files_QListWidget)
        self.welcome_tab_layout.addWidget(self.favorite_files_QListWidget)
        self.welcome_tab_layout.addWidget(self.due_task_QLabel)
        self.welcome_tab_layout.addWidget(self.due_tasks_QListWidget)
        self.welcome_tab_layout.addWidget(self.reset_due_tasks)

        self.set_due_tasks(manage_connection=True)


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

    def write_notes(self):
        pass

    def set_notes(self):
        pass

    def set_favorites(self):
        #clear 
        #query the data from the dict
        #add to the list
        pass

    def set_recent_files(self):
        #clear 
        #query the data from the dict
        #add to the list
        pass
    
    def open_file(self):
        #get path
        #startfile
        pass
#when opened from treeview or

def set_has_favorite(self):
    #open json as write
    #if more than x element(10?)
    #pop first element
    #append to end 
    pass
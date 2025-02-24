from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTableView,QTabWidget,QWidget,QCompleter,QPushButton,QMessageBox,QDialog,QHBoxLayout,QLabel
from PySide6.QtCore import QStringListModel
from PySide6.QtGui import QCursor,QPixmap


import sys

#--- --- Global variables --- ---#




class TestTab (QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1000, 800)
        self.TestTab_layout = QVBoxLayout()
        self.setLayout(self.TestTab_layout)

        self.test_button =QPushButton('test')
        self.test_button.clicked.connect(self.dialog_box_test)
        self.TestTab_layout.addWidget(self.test_button)
        
    def dialog_box_test(self):

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

        #dialog.setWindowIcon(QDialog.question)
       
        if dialog.exec() == 1:
            print(name_query_edit.text())
            print('yes')
        else:
            print('no')


import os
all_files = os.walk(r'C:\Users\laure\OneDrive\Bureau\sauvegarde1')
oldName = 'anat'
newName = 'caiman'

for dirpath, dirnames, filenames in all_files:
    
    for dir_name in dirnames:
        old_path = os.path.join(dirpath, dir_name)
        new_path = os.path.join(dirpath, dir_name.replace(oldName, newName))

        if oldName in dir_name and not os.path.exists(new_path):
            os.rename(old_path, new_path)

    for file_name in filenames:
        old_path = os.path.join(dirpath, file_name)
        new_path = os.path.join(dirpath, file_name.replace(oldName, newName))

        if oldName in file_name and not os.path.exists(new_path):
            os.rename(old_path, new_path)

'''app = QApplication(sys.argv)
window = TestTab()
window.show()
app.exec()'''


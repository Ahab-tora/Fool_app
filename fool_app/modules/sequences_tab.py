
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

class Sequences_tab(QWidget):
    def __init__(self):
        super().__init__()

        self.sequences_layout = QHBoxLayout()
        self.setLayout(self.sequences_layout)

        self.left_sublayout = QVBoxLayout()
        self.sequences_layout.addLayout(self.left_sublayout)
        self.right_sublayout = QHBoxLayout()
        self.sequences_layout.addLayout(self.right_sublayout)

        #--- --- ---
        def sequences_buttons():
            sequences = 'SQ010','SQ020','SQ030','SQ040','SQ050','SQ060','SQ070','SQ820','SQ090','SQ100','SQ110','SQ120','SQ130','SQ140','SQ150','SQ160','SQ170','SQ180','SQ190','SQ200'

            self.sequence_buttons_group = QButtonGroup(self.left_sublayout)
            self.sequence_buttons_group.setExclusive(True)
            self.sequence_buttons_box = QGroupBox('Sequences')
            self.sequence_buttons_box.setStyleSheet("QGroupBox { border: none; }")
            self.sequence_buttons_box_layout = QGridLayout()
            
            self.sequence_buttons_box.setLayout(self.sequence_buttons_box_layout)
            self.left_sublayout.addWidget(self.sequence_buttons_box)


            self.sequence_buttons = {}
            loop_counter = 0
            grid_row = 0
            buttons_per_row = 6
            for sequence in sequences:
                if loop_counter % buttons_per_row == 0:
                    grid_row += 1
                    loop_counter = 0
                self.sequence_buttons[sequence] = QPushButton(sequence)
                self.sequence_buttons[sequence].setCheckable(True)
                self.sequence_buttons[sequence].setStyleSheet("QPushButton:checked { background-color: #5288B2; }")
                self.sequence_buttons_group.addButton(self.sequence_buttons[sequence])                 
                self.sequence_buttons_box_layout.addWidget(self.sequence_buttons[sequence],grid_row,loop_counter)
                loop_counter += 1

            self.current_sequence = None
            self.sequence_buttons_group.buttonClicked.connect(self.set_current_sequence)
            self.sequence_buttons_group.buttonClicked.connect(self.update_shots_view)
        sequences_buttons()

        #need to find a better name
        self.shots_view = Shots_widget(parent_class=self)
        self.left_sublayout.addWidget(self.shots_view)
        #--- --- ---
        self.tabWiget = QTabWidget()
        self.right_sublayout.addWidget(self.tabWiget)

        self.maya_tab = Maya_subtab()
        self.tabWiget.addTab(self.maya_tab,'Maya tab')

        self.houdini_tab = Houdini_subtab()
        self.tabWiget.addTab(self.houdini_tab,'Houdini tab')
        

    def set_current_sequence(self):
        current_sequence = self.sequence_buttons_group.checkedButton().text()
        self.current_sequence = current_sequence

    def update_shots_view(self):
        self.shots_view.set_listView()

    def on_display(self):
        pass


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
        self.listView.setModel(self.model)
        self.shots_layout.addWidget(self.listView)

        #--- --- ---

    #--- --- ---

    def set_listView(self):

        self.model.clear()
        if not self.parent_class.current_sequence:
            return
        

        #requests to get shots of the sequence
        shots = 'SH010','SH020','SH030','SH040','SH050'
        for shot in shots:
            print(shot)
            item = QStandardItem(shot)
            self.model.appendRow(item)


class Maya_subtab(QWidget):
    def __init__(self):
        super().__init__()


class Houdini_subtab(QWidget):
    def __init__(self):
        super().__init__()

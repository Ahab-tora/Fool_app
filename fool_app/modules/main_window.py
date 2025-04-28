
#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTableView,QTabWidget,QWidget,QCompleter,QMessageBox
from PySide6.QtCore import QStringListModel,Qt
from PySide6.QtGui import QCursor,QPixmap

#--- Standard library imports
import sys
import requests
import sqlite3

#--- data imports
import data
from data import global_variables

#--- modules imports
from .treeview_tab import Treeview
from .welcome_tab import Welcome
from .ftrack_tab import Ftrack_tab
#from .assets_tab import Assets_tab
from .tools_tab import Tools_tab
#from .sequences_tab import Sequences_tab
from .elementsTab import ElementsTab

class Fool (QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle("Fool!")
        self.tab_widget = QTabWidget()
        self.tab_widget.setMovable(True) 
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.setDocumentMode(True)


        #we call the tabs
        
        self.welcome_tab = Welcome()
        self.tab_widget.addTab(self.welcome_tab,'Homepage')

        '''self.treeview_tab = Treeview(root_path=global_variables.root_path,table_path= global_variables.tables_path + '\\treeview_table.db')
        self.tab_widget.addTab(self.treeview_tab,'treeview tab')'''
        
        self.ftrack_tab = Ftrack_tab()
        self.tab_widget.addTab(self.ftrack_tab,'ftrack tab')

        self.tools_tab = Tools_tab()
        self.tab_widget.addTab(self.tools_tab,'Tools tab')

        self.sequencesTab = ElementsTab(name='sequences')
        self.tab_widget.addTab(self.sequencesTab,'sequences')

        self.testTab = ElementsTab(name='assets')
        self.tab_widget.addTab(self.testTab,'assets')
        
        self.loaded_tab = self.welcome_tab
        self.tab_widget.currentChanged.connect(self.tab_change)
        

        cursor_path = QPixmap(global_variables.fool_path + '\\icons\\pointer_gauntlet.png')
        self.gauntlet_cursor = QCursor(cursor_path,0,0)
        self.setCursor(self.gauntlet_cursor)

        dark_stylesheet = """
        QMainWindow {
            background-color: #3F3F3F;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #3F3F3F;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #d9d9d9;
            padding: 10px;
            border: 1px solid #444;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: #505050;
        }
        QTabBar::tab:hover {
            background-color: #606060;
        }
        QWidget {
            background-color: #3F3F3F;
            color: #d9d9d9;
            font-size: 14px;
        }
        QPushButton {
            background-color: #444;
            color: #d9d9d9;
            border: 1px solid #555;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #666;
        }
        QLineEdit, QTextEdit {
            background-color: #3c3c3c;
            color: #d9d9d9;
            border: 1px solid #555;
        }
        QTableWidget {
            background-color: #3c3c3c;
            color: #d9d9d9;
            gridline-color: #555;
            border: 1px solid #444;
        }
        QListWidget {
            background-color: #3c3c3c;
            color: #d9d9d9;
            border: 1px solid #555;
        }
        QHeaderView::section {
            background-color: #444;
            color: #d9d9d9;
            padding: 5px;
            border: 1px solid #555;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def tab_change(self):
        
        current_tab = self.tab_widget.currentWidget()
        self.loaded_tab = current_tab
        self.loaded_tab.on_display()
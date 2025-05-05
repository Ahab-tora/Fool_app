#--- --- Imports

#--- PySide6 imports
from PySide6.QtWidgets import QApplication,QMessageBox

#--- Standard library imports
import sys
import requests

#--- data imports
import data
from data import global_variables

#--- modules imports
from modules.main_window import Fool


def checking_server():
    #try to ping
    #if it does not work, message error and return
    #compare versions
    #if the other version is newer, update
    def checking_connection():
        try:
            response = requests.get(f'{global_variables.base_url}/ping',timeout=8)
            #results = response.json()
            #print(results)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f'Could not connect to the server:{e}')
            sys.exit()

    def checking_updates():
        response = requests.get(f'{global_variables.base_url}/version')
        server_version = response.json()
        
        if not server_version == global_variables.version:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Error")
            msg_box.setText('An update is available! Please download it <a href="https://github.com/Ahab-tora/Fool_app/tree/main">here</a> and replace the existing one.')
            msg_box.setTextFormat(Qt.TextFormat.RichText) 
            msg_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)  
            msg_box.exec()

    checking_connection()
    checking_updates()


if __name__ == '__main__':

    print('aah')
    app = QApplication(sys.argv)
    checking_server()
    print('ah!')
    window = Fool()
    print('ahah!')
    window.show()
    print('ah..')
    app.exec()
    print('Closing Fool!')



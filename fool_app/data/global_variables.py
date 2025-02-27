#use UNC path 

#use 2 forward slashes for paths and 4 if it's a storage for the first one
#example : 'C:\\user\\path' , '\\\\Storage\\path'

#for pathes used in maya, use backward slashes and don't double them unless it's a storage
#example : 'C:/code/retopo_tool.py' , '//Storage/retopo_tool.py'
import os

#--- --- Paths

base_url = "http://10.69.240.231:8000/END"



fool_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

'''pipeline_path = '\\\\Storage\\esma\\3D4\\threeLittlePigs'''
#root_path = pipeline_path
#assets_path = '\\04_asset'
#sequences_path = '\\06_shot'

version = '1.0.25022025'

#--- --- Ftrack data

'''server_url = 'https://esma-lyon.ftrackapp.com'
project_name = 'END'
project_users = 'Leriche','Chalmet','Kidangan','Maestracci','VANDERWEYEN','Guinet--Elmi','Kumar','Hatef','NGUYEN'''
api_user = 'e.guinet-elmi@lyn.ecolescreatives.com'


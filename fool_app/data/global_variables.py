#use 2 forward slashes for paths and 4 if it's a storage for the first one
#example : 'C:\\user\\path' , '\\\\Storage\\path'

#for pathes used in maya, use backward slashes and don't double them unless it's a storage
#example : 'C:/code/retopo_tool.py' , '//Storage/retopo_tool.py'
import os

#--- --- Paths

base_url = "http://192.168.56.1:8000/END"
queryUrl = base_url + '/query'
sequences_url = base_url + '/sequences'
assets_url = base_url + '/assets'
fool_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#--- --- Ftrack data
api_user = 'e.guinet-elmi@lyn.ecolescreatives.com'

#--- --- Version
version = '1.0.25022025'



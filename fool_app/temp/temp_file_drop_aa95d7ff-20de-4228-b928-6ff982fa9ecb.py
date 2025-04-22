
import maya.cmds as cmds
def onMayaDroppedPythonFile(*args):
    filePath = 'C:/Users/laure/OneDrive/Bureau/05_shit/SQ0010/SH0010/maya/scenes/anim/edit/instrument.mb'
    namespace = filePath.split('/')[-1][0:-3]
    cmds.file(filePath, reference=True,namespace=namespace)
#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from .packages import BrickBuilderUI as UI

app = adsk.core.Application.get()
ui  = app.userInterface

def run(context):
    try:
        # ui.messageBox('hello')
        UI.run(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        UI.stop(context)
        # ui.messageBox('Stop addin')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import BrickBuilderModel as BB

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
ui  = app.userInterface
commandId = 'BrickBuilderCmd'
workspaceToUse = 'FusionSolidEnvironment'
panelToUse = 'SolidCreatePanel'

# Some utility functions
def commandDefinitionById(id):

    if not id:
        ui.messageBox('commandDefinition id is not specified')
        return None
    commandDefinitions_ = ui.commandDefinitions
    commandDefinition_ = commandDefinitions_.itemById(id)
    return commandDefinition_

def getPanelById(panelId):
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(panelId)
    return toolbarPanel_

def addCommandToPanel(commandId, commandName, commandDescription, commandResources, onCommandCreated):
    commandDefinitions_ = ui.commandDefinitions

    toolbarControlsPanel_ = getPanelById(panelToUse).controls
    toolbarControlPanel_ = toolbarControlsPanel_.itemById(commandId)
    if not toolbarControlPanel_:
        commandDefinitionPanel_ = commandDefinitions_.itemById(commandId)
        if not commandDefinitionPanel_:
            commandDefinitionPanel_ = commandDefinitions_.addButtonDefinition(commandId, commandName, commandDescription, commandResources)

        commandDefinitionPanel_.commandCreated.add(onCommandCreated)

        adsk.core.NamedValues.create()

        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        toolbarControlPanel_ = toolbarControlsPanel_.addCommand(commandDefinitionPanel_, '')
        toolbarControlPanel_.isVisible = True

class BrickBuilderCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs
            builder = BB.BrickBuilderModel()
            for input in inputs:
                if input.id == commandId + '_shape_selection':
                    ui.messageBox('{}'.format(input.selectionCount))
                    builder.shape = input.selection(0).entity
                elif  input.id == commandId + '_brick_selection':
                    builder.part = input.selection(0).entity
                elif  input.id == commandId + '_hollow_checkbox':
                    builder.isHollow = bool(input.value)

            builder.build();
            args.isValidResult = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class BrickBuilderCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class BrickBuilderCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = BrickBuilderCommandExecuteHandler()
            cmd.execute.add(onExecute)
            # onExecutePreview = BrickBuilderCommandExecuteHandler()
            # cmd.executePreview.add(onExecutePreview)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            # handlers.append(onExecutePreview)

            #define the inputs
            inputs = cmd.commandInputs
            # Create selection input
            selectionInput = inputs.addSelectionInput(commandId + '_shape_selection', 'Select Shape', 'Select the Shape Body')
            selectionInput.setSelectionLimits(1, 1)
            selectionInput.addSelectionFilter('Bodies')
            # Create selection input
            selectionInput2 = inputs.addSelectionInput(commandId + '_brick_selection', 'Select Brick', 'Select the Brick Body')
            selectionInput2.setSelectionLimits(1, 1)
            selectionInput2.addSelectionFilter('Bodies')
            # Create bool value input with checkbox style
            inputs.addBoolValueInput(commandId + '_hollow_checkbox', 'Hollow', True, '', True)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def destroyObject(uiObj, objToDelete):
    if uiObj and objToDelete:
        if objToDelete.isValid:
            objToDelete.deleteMe()
        else:
            uiObj.messageBox('objToDelete is not a valid object')

def commandControlByIdForPanel(id):
    global workspaceToUse
    global panelToUse
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(panelToUse)
    toolbarControls_ = toolbarPanel_.controls
    toolbarControl_ = toolbarControls_.itemById(id)
    return toolbarControl_

def run(context):

    # command properties
    commandName = 'Brick Builder'
    commandDescription = 'Turn a Shape Body into Bricks'
    commandResources = './resources'

    # add the new command under "SolidCreate" panel
    addCommandToPanel(commandId, commandName, commandDescription, commandResources, BrickBuilderCommandCreatedHandler())
    # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
    adsk.autoTerminate(False)

def stop(context):
    objArray = []
    commandControl_ = commandControlByIdForPanel(commandId)
    if commandControl_:
        objArray.append(commandControl_)

    commandDefinition_ = commandDefinitionById(commandId)
    if commandDefinition_:
        objArray.append(commandDefinition_)

    for obj in objArray:
        destroyObject(ui, obj)

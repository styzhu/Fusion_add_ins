#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback


def getPanelById(panelId):
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(panelId)
    return toolbarPanel_

class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class BuildBrickCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # Keep the handler referenced beyond this function
            handlers.append(onDestroy)
            inputs = cmd.commandInputs

            # Create selection input
            selectionInput = inputs.addSelectionInput(commandId + '_shape_selection', 'Select Shape', 'Select the Shape Body')
            selectionInput.setSelectionLimits(1, 1)
            # Create selection input
            selectionInput = inputs.addSelectionInput(commandId + '_brick_selection', 'Select Brick', 'Select the Brick Body')
            selectionInput.setSelectionLimits(1, 1)
            # Create bool value input with checkbox style
            inputs.addBoolValueInput(commandId + '_hollow_checkbox', 'Hollow', True, '', True)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

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

def run(context):
    ui = None
    try:
        global app
        global ui
        global commandId
        global commandName
        global commandDescription
        global commandResources
        global handlers
        global workspaceToUse
        global panelToUse
        handlers = []
        commandId = 'BrickBuilder'
        commandName = 'Brick Builder'
        commandDescription = 'Turn a Shape Body into Bricks'
        commandResources = 'resources'
        app = adsk.core.Application.get()
        ui  = app.userInterface
        workspaceToUse = 'FusionSolidEnvironment'
        panelToUse = 'SolidCreatePanel'

        addCommandToPanel(commandId, commandName, commandDescription, commandResources, BuildBrickCommandCreatedHandler())

        ui.messageBox('hello')

        # # Create command defintion
        # cmdDef = ui.commandDefinitions.itemById(commandId)
        # if not cmdDef:
        #     cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription)
        #
        # # Add command created event
        # onCommandCreated = MyCommandCreatedHandler()
        # cmdDef.commandCreated.add(onCommandCreated)
        # # Keep the handler referenced beyond this function
        # handlers.append(onCommandCreated)
        #
        # # Execute command
        # cmdDef.execute()

        # Prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Stop addin')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

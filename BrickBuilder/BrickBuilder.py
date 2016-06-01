#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

app = adsk.core.Application.get()
ui  = app.userInterface
commandId = 'BrickBuilder'
commandName = 'Brick Builder'
commandDescription = 'Turn a Shape Body into Bricks'
commandResources = 'resources'

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

class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
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
            global commandId

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

def run(context):
    ui = None
    try:
        UI.run(context)

        # Create command defintion
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription)

        # Add command created event
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)

        # Execute command
        cmdDef.execute()

        # Prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        UI.stop(context)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

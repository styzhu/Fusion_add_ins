#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback


def getGCD(i_numList):
    """return greatest common divisor of the input numberlist"""
    output = 0
    for i in range(len(i_numList)-1):
        if i == 0:
            output = getPairGCD(i_numList[i], i_numList[i+1])
        else:
            output = getPairGCD(output, i_numList[i+1])
        i += 1
    return output


def getPairGCD(a, b):
    """helper for getGCD() return the GCD of two input numbers"""
    TOL = 0.5
    tmp = max(a, b)
    b = min(a, b)
    a = tmp
    while b%a != 0:
    # while b%a > TOL:
        tmp = a - b
        if tmp > b:
            a = tmp
        else:
            a = b
            b = tmp
    return b

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        root = app.activeProduct.rootComponent

        ui.messageBox('Select the shape')
        sel = ui.selectEntity('Select an object to legolize', \
        'Bodies,SolidBodies, SurfaceBodies, MeshBodies')
        shape = sel.entity
        ui.messageBox('Select the part')
        sel = ui.selectEntity('Select an object to legolize', \
        'Bodies,SolidBodies, SurfaceBodies, MeshBodies')
        part = sel.entity
        # ui.messageBox('name: {}'.format(shape.name))
        boundingBox = shape.boundingBox
# if boundingBox.isValid
        maxPt = boundingBox.maxPoint
        minPt = boundingBox.minPoint

        nominateList = []
        finalList = []
        STEP = 3
        _voxelSize = getGCD([maxPt.x-minPt.x, maxPt.y-minPt.y, maxPt.z-minPt.z])/STEP
        numX = (int)((maxPt.x-minPt.x)/_voxelSize)
        numY = (int)((maxPt.y-minPt.y)/_voxelSize)
        numZ = (int)((maxPt.z-minPt.z)/_voxelSize)
        ui.messageBox('{}\n{}'.format(STEP, maxPt.x-minPt.x))
        ui.messageBox('num: {}'.format(numX*numY*numZ))

        for i in range(numX):
            for j in range(numY):
                for k in range(numZ):
                    pt = adsk.core.Point3D.create(minPt.x+(i+0.5)*_voxelSize,\
                                                  minPt.y+(j+0.5)*_voxelSize,\
                                                  minPt.z+(k+0.5)*_voxelSize)
                    nominateList.append(pt)

        translateMatrix = adsk.core.Matrix3D.create()
        # ui.messageBox('part: \n{}'.format(part))

        partBox = part.boundingBox
        px = partBox.maxPoint.x - partBox.minPoint.x
        py = partBox.maxPoint.y - partBox.minPoint.y
        pz = partBox.maxPoint.z - partBox.minPoint.z

        target = None
        if part.assemblyContext:
            target = part.assemblyContext
        else:
            target = root

        # partPt = adsk.core.Point3D.create(px, py, pz)
        partPt = adsk.core.Vector3D.create(px, py, pz)
        xAxis = adsk.core.Vector3D.create(1, 0, 0)
        yAxis = adsk.core.Vector3D.create(0, 1, 0)
        zAxis = adsk.core.Vector3D.create(0, 0, 1)
        for p in nominateList:
            ptContainVal = shape.pointContainment(p)
            if ptContainVal == 0:
                newBody = part.copyToComponent(target)
                trans = adsk.core.Matrix3D.create()
                trans.translation = adsk.core.Vector3D.create(p.x, p.y, p.z)
                bodyColl = adsk.core.ObjectCollection.create()
                bodyColl.add(newBody)
                moveInput = root.features.moveFeatures.createInput(bodyColl, trans)
                moveFeat = root.features.moveFeatures.add(moveInput)

                # finalList.append(p)
                # ui.messageBox('{}'.format(p))
                # translateMatrix.setToIdentity()
                # translateMatrix.translation = partPt
                # app.activeProduct.rootComponent.occurrences.addExistingComponent(part, translateMatrix)

    except:
        if ui:
            ui.messageBox('Fail:{}'.format(traceback.format_exc()))

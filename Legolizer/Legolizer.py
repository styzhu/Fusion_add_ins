#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math


def getPartNumOnSide(shapeSideLength, partSideLength):
    return math.ceil(shapeSideLength/partSideLength)

def isOdd(num):
    return (num & 1)

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
        shapeBBox = shape.boundingBox
# if shapeBBox.isValid
        shapeLengthX = shapeBBox.maxPoint.x - shapeBBox.minPoint.x
        shapeLengthY = shapeBBox.maxPoint.y - shapeBBox.minPoint.y
        shapeLengthZ = shapeBBox.maxPoint.z - shapeBBox.minPoint.z

        partBBox = part.boundingBox
        partLengthX = partBBox.maxPoint.x - partBBox.minPoint.x
        partLengthY = partBBox.maxPoint.y - partBBox.minPoint.y
        partLengthZ = partBBox.maxPoint.z - partBBox.minPoint.z
        partCenterPt = adsk.core.Point3D.create((partBBox.maxPoint.x + partBBox.minPoint.x)/2,\
                                                (partBBox.maxPoint.y + partBBox.minPoint.y)/2,\
                                                (partBBox.maxPoint.z + partBBox.minPoint.z)/2)

        nominateList = []
        numX = getPartNumOnSide(shapeLengthX, partLengthX)
        numY = getPartNumOnSide(shapeLengthY, partLengthY)
        numZ = getPartNumOnSide(shapeLengthZ, partLengthZ)
        centerPt = adsk.core.Point3D.create((shapeBBox.maxPoint.x + shapeBBox.minPoint.x)/2,\
                                            (shapeBBox.maxPoint.y + shapeBBox.minPoint.y)/2,\
                                            (shapeBBox.maxPoint.z + shapeBBox.minPoint.z)/2)
        if not isOdd(numX):
            centerPt.x = centerPt.x - partLengthX
        if not isOdd(numY):
            centerPt.y = centerPt.y - partLengthY
        if not isOdd(numZ):
            centerPt.z = centerPt.z - partLengthZ
        nominateList.append(centerPt)
        for i in range((math.ceil)(numX/2)):
            for j in range((math.ceil)(numY/2)):
                for k in range((math.ceil)(numZ/2)):
                    pt = adsk.core.Point3D.create(centerPt.x + i * partLengthX,\
                                                  centerPt.y + j * partLengthY,\
                                                  centerPt.z + k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x + i * partLengthX,\
                                                  centerPt.y - j * partLengthY,\
                                                  centerPt.z + k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x + i * partLengthX,\
                                                  centerPt.y + j * partLengthY,\
                                                  centerPt.z - k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x - i * partLengthX,\
                                                  centerPt.y + j * partLengthY,\
                                                  centerPt.z + k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x - i * partLengthX,\
                                                  centerPt.y - j * partLengthY,\
                                                  centerPt.z + k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x + i * partLengthX,\
                                                  centerPt.y - j * partLengthY,\
                                                  centerPt.z - k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x - i * partLengthX,\
                                                  centerPt.y + j * partLengthY,\
                                                  centerPt.z - k * partLengthZ,)
                    nominateList.append(pt)
                    pt = adsk.core.Point3D.create(centerPt.x - i * partLengthX,\
                                                  centerPt.y - j * partLengthY,\
                                                  centerPt.z - k * partLengthZ,)
                    nominateList.append(pt)
        ui.messageBox('num: {}'.format(len(nominateList)))

        ui.messageBox('list: {}'.format(numX))
        ui.messageBox('center: {}, {}, {}'.format(centerPt.x, centerPt.y, centerPt.z))

        translateMatrix = adsk.core.Matrix3D.create()
        # ui.messageBox('part: \n{}'.format(part))

        target = None
        if part.assemblyContext:
            target = part.assemblyContext
        else:
            target = root

        for p in nominateList:
            ptContainVal = shape.pointContainment(p)
            if ptContainVal == 0:
                newBody = part.copyToComponent(target)
                trans = adsk.core.Matrix3D.create()
                trans.translation = adsk.core.Vector3D.create(p.x - partCenterPt.x,\
                                                              p.y - partCenterPt.y,\
                                                              p.z - partCenterPt.z)
                bodyColl = adsk.core.ObjectCollection.create()
                bodyColl.add(newBody)
                moveInput = root.features.moveFeatures.createInput(bodyColl, trans)
                moveFeat = root.features.moveFeatures.add(moveInput)

    except:
        if ui:
            ui.messageBox('Fail:{}'.format(traceback.format_exc()))

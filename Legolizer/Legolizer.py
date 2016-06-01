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
        startPt = adsk.core.Point3D.create(centerPt.x - (math.ceil)(numX/2) * partLengthX,\
                                           centerPt.y - (math.ceil)(numY/2) * partLengthY,\
                                           centerPt.z - (math.ceil)(numZ/2) * partLengthZ)
        for i in range(numX + 1):
            for j in range(numY + 1):
                for k in range(numZ + 1):
                    pt = adsk.core.Point3D.create(startPt.x + i * partLengthX,\
                                                  startPt.y + j * partLengthY,\
                                                  startPt.z + k * partLengthZ)
                    nominateList.append(pt)

        # ui.messageBox('startPt: {}, {}, {}'.format(startPt.x, startPt.y, startPt.z))
        #
        # ui.messageBox('list: {}'.format(numX))
        # ui.messageBox('center: {}, {}, {}'.format(numX, numY, numZ))

        translateMatrix = adsk.core.Matrix3D.create()
        # ui.messageBox('part: \n{}'.format(part))

        target = None
        if part.assemblyContext:
            target = part.assemblyContext
        else:
            target = root

        for p in nominateList:
            # test if point is inside, thus reduce the chance of Fusion's frozen
            p1 = adsk.core.Point3D.create(p.x + partLengthX,\
                                          p.y,\
                                          p.z)
            p2 = adsk.core.Point3D.create(p.x - partLengthX,\
                                          p.y,\
                                          p.z)
            p3 = adsk.core.Point3D.create(p.x,\
                                          p.y + partLengthY,\
                                          p.z)
            p4 = adsk.core.Point3D.create(p.x,\
                                          p.y - partLengthY,\
                                          p.z)
            p5 = adsk.core.Point3D.create(p.x,\
                                          p.y,\
                                          p.z + partLengthZ)
            p6 = adsk.core.Point3D.create(p.x,\
                                          p.y,\
                                          p.z - partLengthZ)
            if (shape.pointContainment(p1) +\
                shape.pointContainment(p2) +\
                shape.pointContainment(p3) +\
                shape.pointContainment(p4) +\
                shape.pointContainment(p5) +\
                shape.pointContainment(p6) == 0):
                continue

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

#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math

class BrickBuilderModel:
    @property
    def shape(self):
        return self._shape
    @shape.setter
    def shape(self, value):
        self._shape = value

    @property
    def part(self):
        return self._part
    @part.setter
    def part(self, value):
        self._part = value

    @property
    def isHollow(self):
        return self._isHollow
    @isHollow.setter
    def isHollow(self, value):
        self._isHollow = value

    def getPartNumOnSide(self, shapeSideLength, partSideLength):
        return math.ceil(shapeSideLength/partSideLength)

    def isOdd(self, num):
        return (num & 1)

    def build(self):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            root = app.activeProduct.rootComponent

            global shape
            global part
            global isHollow
            shape = self.shape
            part = self.part
            isHollow = self.isHollow
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
            numX = self.getPartNumOnSide(shapeLengthX, partLengthX)
            numY = self.getPartNumOnSide(shapeLengthY, partLengthY)
            numZ = self.getPartNumOnSide(shapeLengthZ, partLengthZ)
            centerPt = adsk.core.Point3D.create((shapeBBox.maxPoint.x + shapeBBox.minPoint.x)/2,\
                                                (shapeBBox.maxPoint.y + shapeBBox.minPoint.y)/2,\
                                                (shapeBBox.maxPoint.z + shapeBBox.minPoint.z)/2)
            if not self.isOdd(numX):
                centerPt.x = centerPt.x - partLengthX
            if not self.isOdd(numY):
                centerPt.y = centerPt.y - partLengthY
            if not self.isOdd(numZ):
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

            target = None
            if part.assemblyContext:
                target = part.assemblyContext
            else:
                target = root

            for p in nominateList:
                if isHollow:
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

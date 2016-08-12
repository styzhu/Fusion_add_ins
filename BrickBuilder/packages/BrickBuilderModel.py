#Author-SAAS
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math, time

class BrickBuilderModel:
    @property
    def offsetX(self):
        return self._offsetX
    @offsetX.setter
    def offsetX(self, value):
        self._offsetX = value

    @property
    def offsetY(self):
        return self._offsetY
    @offsetY.setter
    def offsetY(self, value):
        self._offsetY = value

    @property
    def offsetZ(self):
        return self._offsetZ
    @offsetZ.setter
    def offsetZ(self, value):
        self._offsetZ = value

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

    def getFinalList(self, nList, numX, numY, numZ):
        # minPt, maxPt stands for min/max point in the nlist, not the pts for the shape
        hList = []
        for p in nList:
            hList.append(shape.pointContainment(p))

        if not isHollow:
            return hList

        _minPt = nList[0]
        _maxPt = nList[-1]

        _i = 0
        for p in nList:
            if p.x == _minPt.x or p.x == _maxPt.x:
                _i = _i + 1
                continue
            elif p.y == _minPt.y or p.y == _maxPt.y:
                _i = _i + 1
                continue
            elif p.z == _minPt.z or p.z == _maxPt.z:
                _i = _i + 1
                continue

            p1 = nList[_i + (numZ + 1) * (numY + 1)]  # x+1
            p2 = nList[_i - (numZ + 1) * (numY + 1)]  # x-1
            p3 = nList[_i + (numZ + 1)]               # y+1
            p4 = nList[_i - (numZ + 1)]               # y-1
            p5 = nList[_i + 1]                        # z+1
            p6 = nList[_i - 1]                        # z-1
            if (shape.pointContainment(p1) +\
                shape.pointContainment(p2) +\
                shape.pointContainment(p3) +\
                shape.pointContainment(p4) +\
                shape.pointContainment(p5) +\
                shape.pointContainment(p6) == 0):
                hList[_i] = -1
            _i = _i + 1

        return hList

    def build(self):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            root = app.activeProduct.rootComponent

            global shape
            global part
            global isHollow
            global offsetX
            global offsetY
            global offsetZ
            offsetX = self.offsetX
            offsetY = self.offsetY
            offsetZ = self.offsetZ
            shape = self.shape
            part = self.part
            isHollow = self.isHollow
            # ui.messageBox('{}'.format(isHollow))
            shapeBBox = shape.boundingBox
    # if shapeBBox.isValid
            shapeLengthX = shapeBBox.maxPoint.x - shapeBBox.minPoint.x
            shapeLengthY = shapeBBox.maxPoint.y - shapeBBox.minPoint.y
            shapeLengthZ = shapeBBox.maxPoint.z - shapeBBox.minPoint.z

            partBBox = part.boundingBox
            partLengthX = partBBox.maxPoint.x - partBBox.minPoint.x - offsetX
            partLengthY = partBBox.maxPoint.y - partBBox.minPoint.y - offsetY
            partLengthZ = partBBox.maxPoint.z - partBBox.minPoint.z - offsetZ
            partCenterPt = adsk.core.Point3D.create((partBBox.maxPoint.x + partBBox.minPoint.x - offsetX)/2,\
                                                    (partBBox.maxPoint.y + partBBox.minPoint.y - offsetY)/2,\
                                                    (partBBox.maxPoint.z + partBBox.minPoint.z - offsetZ)/2)

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
            startPt = adsk.core.Point3D.create(centerPt.x - (math.ceil)(numX/2) * partLengthX,\
                                               centerPt.y - (math.ceil)(numY/2) * partLengthY,\
                                               centerPt.z - (math.ceil)(numZ/2) * partLengthZ)
            nominateList.append(startPt)
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

            hList = []
            # test if point is inside, thus reduce the chance of Fusion's frozen
            hList = self.getFinalList(nominateList, numX, numY, numZ)

            trans = adsk.core.Matrix3D.create()
            _i = 0
            for p in nominateList:
                if hList[_i] == 0:
                    newBody = part.copyToComponent(target)

                    trans.translation = adsk.core.Vector3D.create(p.x - partCenterPt.x,\
                                                                  p.y - partCenterPt.y,\
                                                                  p.z - partCenterPt.z)
                    bodyColl = adsk.core.ObjectCollection.create()
                    bodyColl.add(newBody)
                    moveInput = root.features.moveFeatures.createInput(bodyColl, trans)
                    moveFeat = root.features.moveFeatures.add(moveInput)
                    # time.sleep(0.1)
                _i = _i + 1

        except:
            if ui:
                ui.messageBox('Fail:{}'.format(traceback.format_exc()))

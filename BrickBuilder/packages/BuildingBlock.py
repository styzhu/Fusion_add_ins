#Author-huanghua
#Description-

import adsk.core, adsk.fusion
from . import config as conf

class BuildingBlock:
    def __init__(self):
        self._lCount = conf.defaultLCount
        self._lengthUnit = conf.defaultLengthUnit
        self._blockPlane = None;
        self._blockPoint = None;
        self._workingComp = None
                
    #properties
    @property
    def workingComponent(self):
        return self._workingComp
    @workingComponent.setter
    def workingComponent(self, value):
        self._workingComp = value
        
    @property
    def lCount(self):
        return self._lCount
    @lCount.setter
    def lCount(self, value):
        self._lCount = value
    
    @property
    def lengthUnit(self):
        return self._lengthUnit
    @lengthUnit.setter
    def lengthUnit(self, value):
        self._lengthUnit = value   
        
    @property
    def blockPlane(self):
        return self._blockPlane
    @blockPlane.setter
    def blockPlane(self, value):
        self._blockPlane = value
        
    @property
    def blockPoint(self):
        return self._blockPoint
    @blockPoint.setter
    def blockPoint(self, value):
        self._blockPoint = value
        
    def _rootComponent(self):
        app = adsk.core.Application.get()
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        return design.rootComponent
        
    def _createNewComponent(self):
        allOccs = self._rootComponent().occurrences
        newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
        return newOcc.component
    
    def _makeExtrude(self, profile, booleanType):
        if profile is None:
            return None
        extrudes = self.workingComponent.features.extrudeFeatures
        extInput = extrudes.createInput(profile, booleanType)

        extDistInput = adsk.core.ValueInput.createByString('length')
        extInput.setDistanceExtent(False, extDistInput)
        return extrudes.add(extInput)

    def _addRectangle(self, sketch, x, y):
        if sketch is None:
            return
        sketchPoint1 = sketch.sketchPoints.add(adsk.core.Point3D.create(0, 0, 0))
        sketchPoint2 = sketch.sketchPoints.add(adsk.core.Point3D.create(x, 0, 0))
        sketchPoint3 = sketch.sketchPoints.add(adsk.core.Point3D.create(x, y, 0))
        sketchPoint4 = sketch.sketchPoints.add(adsk.core.Point3D.create(0, y, 0))
        line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(sketchPoint1, sketchPoint2)
        line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(sketchPoint2, sketchPoint3)
        line3 = sketch.sketchCurves.sketchLines.addByTwoPoints(sketchPoint3, sketchPoint4)
        line4 = sketch.sketchCurves.sketchLines.addByTwoPoints(sketchPoint4, sketchPoint1)
        sketch.geometricConstraints.addHorizontal(line1)
        sketch.geometricConstraints.addVertical(line2)
        sketch.geometricConstraints.addParallel(line1, line3)
        sketch.geometricConstraints.addParallel(line2, line4)
        dimension1 = sketch.sketchDimensions.addOffsetDimension(line1, line3, adsk.core.Point3D.create(0, 0, 0))
        dimension2 = sketch.sketchDimensions.addOffsetDimension(line2, line4, adsk.core.Point3D.create(x, y, 0))
        dimension1.parameter.expression = 'length';
        dimension2.parameter.expression = 'length';
    
    def __validateInput(self):
        app = adsk.core.Application.get()
        ui = app.userInterface
        if self.lCount <= 0 or self.lengthUnit <= 0:
            ui.messageBox('invalid parameters')
            return False
        if self.blockPlane == None:
            return False;
        return True
    
    def __prepareComponent(self, needNewComp):
        app = adsk.core.Application.get()
            
        if needNewComp:
            self.workingComponent = self._createNewComponent()
        else:
            self.workingComponent = self._rootComponent()
            
        if self.workingComponent is None:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox('New component failed to create', 'New Component Failed')
            return False
        return True
        
    def build(self, needNewComp=False):

        if not self.__validateInput():
            return
            
        if not self.__prepareComponent(needNewComp):
            return
        sketch = self.workingComponent.sketches.add(self.blockPlane)

        length = self.lCount*self.lengthUnit
        if sketch.profiles.count == 0:
            self._addRectangle(sketch, length, length)
        
        # Create the base plate per input
        baseExt = self._makeExtrude(sketch.profiles[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        srcBody = self.workingComponent.bRepBodies[0];
        #srcBody.copyToComponent(self.workingComponent)
            
    @staticmethod
    def as_buildingblock(dct, needNewComp = False):
        if 'lCount' in dct and 'lengthUnit' in dct:
            bb = BuildingBlock()
            bb.lCount = dct['lCount']
            bb.lengthUnit = dct['lengthUnit']
            return bb
        return dct
         
    def toJson(self):
        return {"lCount":self._lCount, "lengthUnit":self._lengthUnit}
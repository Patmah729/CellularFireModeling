# -*- coding: utf-8 -*-

import arcpy
import ModelFire, DeriveFuel

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Fire Modeling"
        self.alias = "ArcAutoFire"

        # List of tool classes associated with this toolbox
        self.tools = [ArcAutoFire,DeriveFuelModel]

class ArcAutoFire:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Model Fire"
        self.description = "Model wildland fires using a frontal cellular automaton"

    def getParameterInfo(self):
        #Define parameter definitions

        # fuel model input
        fuelModel = arcpy.Parameter(
            displayName="Input Fuel Model",
            name="in_features",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
        
        #Barrier features input
        barriers = arcpy.Parameter(
            displayName="Barrier Features",
            name="barriers",
            datatype="DEFeatureClass",
            parameterType="Optional",
            direction="Input")
        
        # Ignition Point(s)
        ignitions = arcpy.Parameter(
            displayName="Ignition Point(s)",
            name="ignitions",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        # DEM input
        dem = arcpy.Parameter(
            displayName="Input Elevation Raster",
            name="dem",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        # Wind parameters
        windDir = arcpy.Parameter(
            displayName="Wind Direction (Degrees)",
            name="windDir",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        #windDir.value = 0
        #windDir.filters = ["CodedValue", "Range"]
        #windDir.filters[0].list = ["MIN", "MAX"]
        #windDir.filters[1].list = [0, 359]

        windSp = arcpy.Parameter(
            displayName="Wind Speed (Meters per Second)",
            name="windSp",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        #windSp.value = 0
        #windSp.filters = ["CodedValue", "Range"]
        #windSp.filters[0].list = ["MIN", "MAX"]
        #windSp.filters[1].list = [0, 32.7]

        # Output
        output = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="DEGeodatasetType",
            parameterType="Required",
            direction="Output")
        
        cellSize = arcpy.Parameter(
            displayName="Cell Size",
            name="cellSize",
            datatype="GPDouble",
            parameterType="Required",
            direction="Output")
        iterations = arcpy.Parameter(
            displayName="Number of Iterations",
            name="iterations",
            datatype="GPDouble",
            parameterType="Required",
            direction="Output")
        iterations.value = 1

        params = [fuelModel, dem, barriers, ignitions, windDir, windSp, output, cellSize, iterations]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        ModelFire.execute(parameters)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

#NOT YET IMPLEMENTED
class DeriveFuelModel:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Derive Fuel Model"
        self.description = "Derive a fuel model for use in ArcAutoFire functions"

    def getParameterInfo(self):
        #Define parameter definitions

        # First parameter
        param0 = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Sinuosity Field",
            name="sinuosity_field",
            datatype="Field",
            parameterType="Optional",
            direction="Input")

        param1.value = "sinuosity"

        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        param2.parameterDependencies = [param0.name]
        param2.schema.clone = True

        params = [param0, param1, param2]

        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        DeriveFuel.execute(parameters)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
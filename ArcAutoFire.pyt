# -*- coding: utf-8 -*-
import arcpy, os, importlib
import ModelFire

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Fire Modeling"
        self.alias = "ArcAutoFire"

        # List of tool classes associated with this toolbox
        self.tools = [ArcAutoFire]

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
        # DEM input
        dem = arcpy.Parameter(
            displayName="Input DEM",
            name="dem",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")        

        #Barrier features input
        barriers = arcpy.Parameter(
            displayName="Barrier Features",
            name="barriers",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input")
        
        # Ignition Point(s)
        ignitions = arcpy.Parameter(
            displayName="Ignition Point(s)",
            name="ignitions",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        # Wind parameters
        windDir = arcpy.Parameter(
            displayName="Wind Direction (Degrees)",
            name="windDir",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        windDir.value = 0
        windDir.filters = ["Range"]
        windDir.filters[0].list = [0, 359]

        windSp = arcpy.Parameter(
            displayName="Wind Speed (Meters per Second)",
            name="windSp",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        windSp.value = 5
        #windSp.filters = ["CodedValue", "Range"]
        #windSp.filters[0].list = ["MIN", "MAX"]
        #windSp.filters[1].list = [0, 32.7]
        
        iterations = arcpy.Parameter(
            displayName="Number of Iterations",
            name="iterations",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        iterations.value = 1

        #probably should just grab these from the environment but this is fine for now
        extent = arcpy.Parameter(
            displayName="Extent",
            name="extent",
            datatype="GPExtent",
            parameterType="Required",
            direction="Input")
        cellSize = arcpy.Parameter(
            displayName="Cell Size",
            name="cellSize",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
             
        # Output
        output = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Output")            

        params = [fuelModel, dem, barriers, ignitions, windDir, windSp, output,  iterations, cellSize, extent]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        fuel = parameters[0]
        output = parameters[6]

        if fuel.value and not output.altered:
            desc = arcpy.Describe(fuel.value)

            # get dataset path
            path = desc.catalogPath

            # if input is inside a geodatabase, go UP one level
            if ".gdb" in path:
                gdb_index = path.lower().find(".gdb")
                folder = os.path.dirname(path[:gdb_index + 4])
            else:
                folder = os.path.dirname(path)

            # clean base name
            name = os.path.splitext(os.path.basename(path))[0]
            print(name)
            # build output gdb path
            output.value = os.path.join(folder, name + "_fire.gdb")

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        gdb_path = parameters[6].valueAsText

        if not arcpy.Exists(gdb_path):
            folder = os.path.dirname(gdb_path)
            name = os.path.basename(gdb_path)
            arcpy.AddMessage(folder)
            arcpy.AddMessage(f"Creating GDB at: {gdb_path}")
            arcpy.management.CreateFileGDB(out_folder_path=folder, 
                                           out_name=name)
        
        importlib.reload(ModelFire)
        arcpy.AddMessage("Reloaded ModelFire module before execution.")
        ModelFire.execute(parameters)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    

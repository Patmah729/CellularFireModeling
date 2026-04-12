import arcpy, arcgis, scipy, numpy as np

def unifyData(parameters): #unify all raster datasets: ensure cells line up, set data to the same extent, convert rasters to numpy arrays, etc.
    cellsize = float(parameters[8].value)
    
    extent = parameters[-1].value
    llc = arcpy.Point(extent.XMin, extent.YMin)

    arcpy.env.extent = extent
    arcpy.env.cellSize = cellsize
    arcpy.env.snapRaster = parameters[0].value
    arcpy.env.outputCoordinateSystem = parameters[0].value

    unifiedData = []

    for param in parameters:
        if param.datatype == "GPDouble":
            unifiedData.append(param.value)
        elif param.datatype == "GPRasterLayer":
            resampled = arcpy.management.Resample(resampling_type="NEAREST",
                                                  in_raster=param.value,
                                                  out_raster="in_memory\\resampled",
                                                  cell_size=arcpy.env.cellSize)
            
            reprojected = arcpy.management.ProjectRaster(in_raster=resampled,
                                                         out_raster="in_memory\\projected",
                                                         out_coor_system=arcpy.env.outputCoordinateSystem)
            
            clip_extent = (f"{extent.XMin} {extent.YMin} {extent.XMax} {extent.YMax}")

            cut = arcpy.management.Clip(in_raster=reprojected,
                                        rectangle=clip_extent,
                                        out_raster="in_memory\\clipped")
            
            array = arcpy.RasterToNumPyArray(in_raster=cut,
                                             lower_left_corner=llc)
            
            unifiedData.append(array)
        elif param.datatype == "GPFeatureLayer":
            rastered = arcpy.conversion.FeatureToRaster(in_features=param.value,
                                                        field="OBJECTID",
                                                        out_raster="in_memory\\rastered",
                                                        cell_size=arcpy.env.cellSize)
            unifiedData.append(rastered)

    return unifiedData
        

def setNeighborhood(windSp, windDir, cellSize):
    """
    Returns a directional kernel for fire spread.

    windSp: wind speed (m/s)
    windDir: direction in degrees (0 = north)
    cellSize: meters
    """

    size = 11 
    center = size // 2

    kernel = np.zeros((size, size))

    theta = np.deg2rad(90-windDir)

    for i in range(size):
        for j in range(size):
            dx = j - center
            dy = center - i  # flip so +y = north

            if dx == 0 and dy == 0:
                continue

            # distance from center
            dist = np.sqrt(dx**2 + dy**2)

            # angle of this neighbor
            angle = np.arctan2(dy, dx)

            # alignment with wind (-1 to 1)
            alignment = np.cos(angle - theta)

            # base decay with distance
            base = np.exp(-dist)

            # wind effect (stronger forward, weaker backward)
            wind_effect = 1 + (windSp / cellSize) * alignment

            # clamp to avoid negatives
            wind_effect = max(0, wind_effect)

            kernel[i, j] = base * wind_effect

    # normalize
    total = kernel.sum()
    if total > 0:
        kernel /= total

    return kernel

def execute(parameters):
    outputs = []
    fixedParams = unifyData(parameters)
    iterations = fixedParams[8]
    #select neighborhoods
    kernel = setNeighborhood(fixedParams[5],fixedParams[4],fixedParams[7])
    
    last30 = None #arcpy.NumPyArrayToRaster(d)
    outputs.append(last30)

    return fixedParams


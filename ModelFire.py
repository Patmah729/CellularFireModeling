import arcpy, arcgis, scipy, numpy as np

def unifyData(parameters): #unify all raster datasets: ensure cells line up, set data to the same extent, convert rasters to numpy arrays, etc.
    cellsize = int(parameters[8].valueAsText)
    unifiedData = []
    extent = parameters[len(parameters)-1]
    llc = extent.lowerLeft

    for i in parameters:
        if type(parameters[i].datatype) == "GPDouble":
            unifiedData.append(parameters[i].value)
        elif type(parameters[i].datatype) == "DERasterDataset":
            resampled = arcpy.management.Resample(resampling_type="NEAREST",
                                                  in_raster=parameters[i].value,
                                                  cell_size=cellsize)
            reprojected = arcpy.management.Project(in_dataset=resampled,
                                                   out_coor_system=extent.spatial_reference)
            cut = arcpy.management.Clip(in_raster=reprojected,
                                        clipping_geometry=extent.polygon
                                        )
            fixedNPA = arcpy.RasterToNumPyArray(in_raster=cut,
                                     lower_left_corner=llc)
            unifiedData.append(fixedNPA)

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

    # theta = np.deg2rad(90-windDir)

    # for i in range(size):
    #     for j in range(size):
    #         dx = j - center
    #         dy = center - i  # flip so +y = north

    #         if dx == 0 and dy == 0:
    #             continue

    #         # distance from center
    #         dist = np.sqrt(dx**2 + dy**2)

    #         # angle of this neighbor
    #         angle = np.arctan2(dy, dx)

    #         # alignment with wind (-1 to 1)
    #         alignment = np.cos(angle - theta)

    #         # base decay with distance
    #         base = np.exp(-dist)

    #         # wind effect (stronger forward, weaker backward)
    #         wind_effect = 1 + (windSp / cellSize) * alignment

    #         # clamp to avoid negatives
    #         wind_effect = max(0, wind_effect)

    #         kernel[i, j] = base * wind_effect

    # # normalize
    # total = kernel.sum()
    # if total > 0:
    #     kernel /= total

    return kernel

def execute(parameters):
    outputs = []
    fixedParams = unifyData(parameters)
    iterations = parameters[7].valueAsText*30
    #select neighborhoods
    kernel = setNeighborhood(parameters[5].value,parameters[4].value,parameters[7].value)

    last30 = None #arcpy.NumPyArrayToRaster(d)
    outputs.append(last30)

    return outputs


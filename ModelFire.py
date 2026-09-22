#(lines 20-62, 85-97)
import arcpy, numpy, scipy, os


def unifyData(parameters): #unify all raster datasets: ensure cells line up, set data to the same extent, convert rasters to numpy arrays, etc.
    cellsize = float(parameters[9].value)
    
    extent = parameters[10].value
    llc = arcpy.Point(extent.XMin, extent.YMin)

    fuel_raster_obj = parameters[0].value
    fuel_raster_path = parameters[0].valueAsText
    dem_raster = parameters[1].valueAsText
    barrier_features = parameters[2].valueAsText if parameters[2].value else None
    ignition_features = parameters[3].valueAsText

    snap_source = None
    snap_source_desc = None

    if fuel_raster_path and fuel_raster_path not in ["#", ""]:
        #arcpy.AddMessage(f"Checking fuel raster path exists: {fuel_raster_path}")
        if arcpy.Exists(fuel_raster_path):
            snap_source = fuel_raster_path
            snap_source_desc = arcpy.Describe(fuel_raster_path)
        else:
            arcpy.AddMessage("Fuel raster path does not exist; will try object fallback.")

    if snap_source is None and fuel_raster_obj is not None:
        try:
            arcpy.AddMessage("Creating arcpy.Raster from fuel_raster_obj fallback.")
            raster_obj = arcpy.Raster(fuel_raster_obj)
            snap_source = raster_obj
            snap_source_desc = arcpy.Describe(raster_obj)
        except Exception as ex:
            arcpy.AddMessage(f"Failed to construct arcpy.Raster from fuel_raster_obj: {ex}")
            snap_source = None

    if snap_source is None:
        raise ValueError("Fuel raster inumpyut is not valid or could not be resolved for snapRaster.")

    arcpy.env.extent = extent
    arcpy.env.cellSize = cellsize
    #arcpy.AddMessage(f"Setting snapRaster to: {snap_source}")

    try:
        arcpy.env.snapRaster = snap_source
    except Exception as ex:
        arcpy.AddMessage(f"snapRaster assignment failed for {snap_source}: {ex}")
        arcpy.AddMessage("Skipping snapRaster assignment and continuing without it.")
        snap_source = None

    if snap_source is not None:
        arcpy.env.outputCoordinateSystem = snap_source_desc.spatialReference
    else:
        arcpy.env.outputCoordinateSystem = arcpy.Describe(dem_raster).spatialReference
        arcpy.AddMessage("Using DEM spatial reference because snapRaster could not be set.")

    def _to_raster(raster_or_result):
        if hasattr(raster_or_result, 'getOutput'):
            raster_or_result = raster_or_result.getOutput(0)
        return arcpy.Raster(raster_or_result)

    data = {}

    # Fuel model
    resampled = arcpy.management.Resample(resampling_type="NEAREST",
                                          in_raster=fuel_raster_obj,
                                          out_raster="in_memory\\fuel_resampled",
                                          cell_size=arcpy.env.cellSize)
    resampled = _to_raster(resampled)
    
    reprojected = arcpy.management.ProjectRaster(in_raster=resampled,
                                                 out_raster="in_memory\\fuel_projected",
                                                 out_coor_system=arcpy.env.outputCoordinateSystem)
    reprojected = _to_raster(reprojected)
    
    clip_extent = (f"{extent.XMin} {extent.YMin} {extent.XMax} {extent.YMax}")

    cut = arcpy.management.Clip(in_raster=reprojected,
                                rectangle=clip_extent,
                                out_raster="in_memory\\fuel_clipped")
    cut = _to_raster(cut)
    
    # Debug raster properties before conversion
    try:
        data['fuel'] = arcpy.RasterToNumPyArray(in_raster=cut, lower_left_corner=llc)
        #arcpy.AddMessage(f"Fuel array shape: {data['fuel'].shape}, dtype: {data['fuel'].dtype}, range: {data['fuel'].min()}-{data['fuel'].max()}")
    except Exception as e:
        arcpy.AddMessage(f"Error converting fuel raster: {e}")
        # Try without lower_left_corner
        try:
            data['fuel'] = arcpy.RasterToNumPyArray(in_raster=cut)
            arcpy.AddMessage("Converted without lower_left_corner")
        except Exception as e2:
            arcpy.AddMessage(f"Still failed: {e2}")
            raise

    # DEM
    resampled = arcpy.management.Resample(resampling_type="NEAREST",
                                          in_raster=dem_raster,
                                          out_raster="in_memory\\dem_resampled",
                                          cell_size=arcpy.env.cellSize)
    resampled = _to_raster(resampled)
    
    reprojected = arcpy.management.ProjectRaster(in_raster=resampled,
                                                 out_raster="in_memory\\dem_projected",
                                                 out_coor_system=arcpy.env.outputCoordinateSystem)
    reprojected = _to_raster(reprojected)
    
    cut = arcpy.management.Clip(in_raster=reprojected,
                                rectangle=clip_extent,
                                out_raster="in_memory\\dem_clipped")
    cut = _to_raster(cut)
    
    data['dem'] = arcpy.RasterToNumPyArray(in_raster=cut, lower_left_corner=llc)

    # Calculate slope
    slope_raster = arcpy.sa.Slope(in_raster=cut, output_measurement="DEGREE")
    slope_raster = arcpy.management.Clip(in_raster=slope_raster,
                                         rectangle=clip_extent,
                                         out_raster="in_memory\\slope_clipped")
    slope_raster = _to_raster(slope_raster)
    data['slope'] = arcpy.RasterToNumPyArray(in_raster=slope_raster, lower_left_corner=llc)

    # Calculate aspect
    aspect_raster = arcpy.sa.Aspect(in_raster=cut)
    aspect_raster = arcpy.management.Clip(in_raster=aspect_raster,
                                          rectangle=clip_extent,
                                          out_raster="in_memory\\aspect_clipped")
    aspect_raster = _to_raster(aspect_raster)
    data['aspect'] = arcpy.RasterToNumPyArray(in_raster=aspect_raster, lower_left_corner=llc)

    # Barriers
    if barrier_features:
        rastered = arcpy.conversion.FeatureToRaster(in_features=barrier_features,
                                                    field="OBJECTID",
                                                    out_raster="in_memory\\barriers_rastered",
                                                    cell_size=arcpy.env.cellSize)
        rastered = _to_raster(rastered)
        # Clip and convert to array
        cut = arcpy.management.Clip(in_raster=rastered,
                                    rectangle=clip_extent,
                                    out_raster="in_memory\\barriers_clipped")
        cut = _to_raster(cut)
        data['barriers'] = arcpy.RasterToNumPyArray(in_raster=cut, lower_left_corner=llc)
    else:
        data['barriers'] = numpy.zeros_like(data['fuel'])

    # Ignitions
    rastered = arcpy.conversion.FeatureToRaster(in_features=ignition_features,
                                                field="OBJECTID",
                                                out_raster="in_memory\\ignitions_rastered",
                                                cell_size=arcpy.env.cellSize)
    rastered = _to_raster(rastered)
    cut = arcpy.management.Clip(in_raster=rastered,
                                rectangle=clip_extent,
                                out_raster="in_memory\\ignitions_clipped")
    cut = _to_raster(cut)
    
    data['ignitions'] = arcpy.RasterToNumPyArray(in_raster=cut, lower_left_corner=llc)
    data['windDir'] = parameters[4].value
    data['windSp'] = parameters[5].value
    data['output'] = parameters[6].valueAsText
    data['iterations'] = int(parameters[7].value)
    data['cellSize'] = cellsize
    data['extent'] = extent
    data['llc'] = llc
    data['timestep'] = parameters[8].value
    return data
        
def converta13(fuel_array):

    #spread TO rates: how easily a neighbor ignites
    fuel_model_to_rates = {
        1: 1.0,
        2: 0.9,
        3: 1.0,
        4: 0.7,
        5: 0.8,
        6: 0.7,
        7: 0.9,
        8: 0.6,
        9: 0.7,
        10: 0.6,
        11: 0.8,
        12: 0.7,
        13: 0.6}
    
    # Create output array
    spreadto_rates = numpy.zeros_like(fuel_array, dtype=float)
    
    for model_id, rate in fuel_model_to_rates.items():
        spreadto_rates[fuel_array == model_id] = rate
    
    # extra barriers
    spreadto_rates[fuel_array == 0] = 0.0      # No fuel
    spreadto_rates[fuel_array == 99] = 0.0     # Water/Non-burnable
    spreadto_rates[fuel_array > 13] = 0.0      # Invalid values

    
    fuel_model_fromrates = { # how strongly a burning cell ignites neighbors, essentially how hot it's burning
                        1: 0.4,
                        2: 0.5,
                        3: 0.6,
                        4: 0.8,
                        5: 0.8,
                        6: 0.7,
                        7: 0.9,
                        8: 1.0,
                        9: 0.9,
                        10: 0.9,
                        11: 1.0,
                        12: 1.0,
                        13: 1.0}
    
    spreadfrom_rates = numpy.zeros_like(fuel_array, dtype=float)
    for model_id, rate in fuel_model_fromrates.items():
        spreadfrom_rates[fuel_array == model_id] = rate
    
    spreadfrom_rates[fuel_array == 0] = 0.0      # No fuel
    spreadfrom_rates[fuel_array == 99] = 0.0     # Water/Non-burnable
    spreadfrom_rates[fuel_array > 13] = 0.0      # Invalid values

    return spreadto_rates, spreadfrom_rates

def execute(parameters):
    data = unifyData(parameters)
    
    # initialize state grid
    state = numpy.zeros_like(data['fuel'], dtype=int)
    
    # ignition points
    state[data['ignitions'] > 0] = 1
    
    # convert fuel model to spread rate multipliers
    fuel_converted = converta13(data['fuel'])
    fuel_spreadto = fuel_converted[0]
    fuel_spreadfrom = fuel_converted[1]

    # Log fuel model statistics
    unique_models = numpy.unique(data['fuel'])
    unique_models = unique_models[unique_models > 0]  # Exclude 0/NODATA
    # arcpy.AddMessage(f"Fuel spread rates range: {fuel_spreadto.min():.3f} - {fuel_spreadto.max():.3f}")
    # arcpy.AddMessage(f"Fuel from rates range: {fuel_spreadfrom.min():.3f} - {fuel_spreadfrom.max():.3f}")

    #barrier mask
    barrier_mask = (data['barriers'] == 0) & (fuel_spreadto > 0)
    max_burn_age = numpy.where(data['fuel'] > 0,
                            (120 * fuel_spreadfrom),  # 10 to 120 minutes
                            0.0)
    burn_age = numpy.zeros_like(data['fuel'], dtype=float)

    # Adjust this parameter for smoother outputs for gifs. keep at 30 for final vers
    timestep = int(data['timestep'])

    # Track drying influence: being near a fire for longer makes it more likely to ignite
    drying_influence = 0.5
    
    for user_iteration in range(data['iterations']):
        arcpy.AddMessage(f"Running input iteration {user_iteration + 1}/{data['iterations']} ({timestep*(user_iteration+1)} simulated minutes)")

        for internal_iter in range(timestep):
            burn_age[state == 1] += 1.0
            burned_out = (burn_age >= max_burn_age) & (state == 1)
            state[burned_out] = 2
            spread_potential = numpy.zeros_like(state, dtype=float)
            drying_influence = numpy.zeros_like(state, dtype=float)
            burning_cells = numpy.where(state == 1)
            for idx in range(len(burning_cells[0])):
                cy, cx = burning_cells[0][idx], burning_cells[1][idx]
                
                # neighbor loop (eventiually replace with convolution)
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = cy + dy, cx + dx
                        
                        if ny < 0 or ny >= state.shape[0] or nx < 0 or nx >= state.shape[1]:
                            continue
                        if state[ny, nx] != 0:
                            continue
                        if not barrier_mask[ny, nx]:
                            continue
                        
                        # TWEAK THESE PARAMETERS \/ \/ \/ \/ \/ \/ \/ \/ \/ \/
                        
                        # Wind influence (1.0 downwind, 0.2 crosswind, 0.05 upwind)
                        neighbor_angle = numpy.arctan2(dy, dx)
                        wind_angle = numpy.deg2rad(data['windDir']-90)
                        alignment = numpy.cos(neighbor_angle - wind_angle)
                        if abs(alignment) > 0.707:  # Within 45° of wind direction
                            windDir_influence = 1.0 if alignment > 0 else 0.1
                        else:
                            windDir_influence = 0.05
                        
                        # aspect
                        cell_aspect = data['aspect'][cy, cx]  # Degrees from north
                        neighbor_dir = (numpy.degrees(numpy.arctan2(dy, dx)) + 360) % 360  # 0-360 degrees
                        aspect_diff = abs(cell_aspect - neighbor_dir)%360
                        if aspect_diff < 45:  # downslope
                            aspect_influence = 0.00
                        elif aspect_diff < 135:  #cross-slope
                            aspect_influence = 0.5
                        else:  
                            aspect_influence = 1.0 #upslope
                    
                        slope_deg = data['slope'][cy, cx]
                        slope_influence = 1.0 if slope_deg > 25 else max(0.2, slope_deg / 25.0)
                        
                        fuelto_influence = fuel_spreadto[ny, nx]
                        fuelfrom_influence = fuel_spreadfrom[cy, cx]
                        nondirectionalWind = data['windSp']*3 #crude conversion to feet per second, 
                        # FORMULAs OF MAGIC! THIS IS WHERE THE BIG TWEAKING HAPPENS
                        # TEST IMPLEMENTATION OF THE ROTHERMAL FIRE SPREAD FORMULA
                        rothermal_influence = (windDir_influence)*(fuelfrom_influence*(1+nondirectionalWind+(aspect_influence/slope_influence)))/(fuelto_influence*(1-drying_influence[ny,nx]))
                        spread_potential[ny,nx] =+ rothermal_influence/data['cellSize']
                        # Increase drying 
                        drying_influence[ny,nx] = min(1.0, drying_influence[ny, nx] + 0.05)
                        #debug log for one-cell outputs
                        #arcpy.AddMessage(f"Cell ({cy},{cx}) -> ({ny},{nx}): wind {windDir_influence:.2f}, aspect {aspect_influence:.2f}, slope {slope_influence:.2f}, fuelto {fuelto_influence:.2f}, fuelfrom {fuelfrom_influence:.2f}")
            
            # transition rule
            max_potential = spread_potential.max()
            mean = spread_potential.mean()
            # debug message if there's weird spread
            # arcpy.AddMessage(f"Max spread potential this step: {max_potential:.4f}, with mean: {mean:.4f}")
            if max_potential > 0:
                random_threshold = numpy.random.random(spread_potential.shape)#*max_potential
                new_ignitions = (spread_potential > random_threshold) & (state == 0) & barrier_mask
                state[new_ignitions] = 1
                burn_age[new_ignitions] = 0.0

        # Save one raster per user iteration (after timestep internal minutes)
        # Create display array: barriers = -1, unburned = 0, burning = 1, burned = 2
        display_state = state.copy().astype(numpy.int8)
        display_state[~barrier_mask] = 3  # Barriers marked as 3
        display_state[state == 0] = 4  # mask for visualization THIS BREAKS THE GIF COLOR MAPPING, FIX LATER
        display_state[state ==1] = 0
        display_state[state == 2] = 1
        # create output raster
        viz_raster = arcpy.NumPyArrayToRaster(display_state,
                                              lower_left_corner=data['llc'],
                                              x_cell_size=data['cellSize'],
                                              y_cell_size=data['cellSize'],
                                              value_to_nodata=None)
        
        viz_path = os.path.join(data['output'], f"fire_visualization_{user_iteration + 1}")
        arcpy.management.CopyRaster(viz_raster, viz_path)
        
        # symbology
        # first is full symbology for reference, second is simplified for better layout creation w/ transparency, but breaks gif mapping.
        colormap_content = """ 
                            0 211 255 190
                            1 255 85 0
                            2 115 0 0
                            3 197 0 255
                            4 211 255 190
                            """
        colormap_content =  """
                            0 255 85 0
                            1 115 0 0
                            """
        
        clr_file = os.path.join(data['output'], f"fire_colormap_{user_iteration + 1}.clr")
        with open(clr_file, 'w') as f:
            f.write(colormap_content)
        
        arcpy.management.AddColormap(viz_path, "#", clr_file)

    return data


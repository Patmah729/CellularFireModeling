import arcpy, arcgis, scipy, numpy

# function to create the neighborhood kernel for the front of the fire.
# should work best at speeds around 5m/s which works out to 1 cell of likely forward fire movement per minute. 
# Higher speeds will create the likelihood of skipping cells and creating temporary holes in the data, which
# shouldn't be too unrealistic, but might not function super well. Beyond 40 kmph (10.7m/s), 
# this begins to underestimate forward spread (Alexander and Cruz. 2019).
def unifyData(parameters):
    unifiedData = []
    #unify all raster datasets: ensure cells line up, set data to the same extent (parameters[9]), etc.
def setNeighborhood(windSp, windDir, cellSize):
    magnitude = windSp*60/cellSize #the number of cells forward the neighborhood should go (the skew of the ellipse)
    ellipse
    neighborGrid =  [[]] #need to figure out the function to turn an ellipse into a kernel grid
    

    radiativeNeighborhood = [[1,1,1], #3x3 moore's neighborhood for direct spread potential, 
                             [1,0,1], #this will be very relatively small per Grishin et al 2002,
                             [1,1,1]] #Mindykowski et al 2011, McAllister er al 2012, and Baranovskiy et al 2022
    dryingNeighborhood = [[0,1,1,1,0], #5x5 circular neighborhood exclusively used to create the shadow of all updating cells
                          [1,1,1,1,1],
                          [1,1,0,1,1],
                          [1,1,1,1,1],
                          [0,1,1,1,0]]
    totalneighborhood = d

    return

def execute(parameters):
    fixedParams = unifyData(parameters)
    iterations = parameters[8]*30
    #select neighborhoods
    kernel = setNeighborhood(parameters[5],parameters[4],parameters[7])
    #generate the shadow over the image using the 5x5 union of the neighborhoods

    return


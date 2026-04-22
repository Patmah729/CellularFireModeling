# ArcAutoFire

Project Produced by Patrick Maher for GRG470C at UT Austin, taught by Dr. Arima in Spring 2026. 

A GIS-Based cellular automata model of wildland fire spread.

Produces a series of raster outputs showing a modeled fire based on surface vegetation, terrain factors, and wind parameters. Example model output is 6 hours of simulated fire spread in the conditions of the June 2022 Dempsey Fire in Palo Pinto, Texas.
To use, add this toolbox to your ArcGIS Pro project.

Ensure you don't use any raw raster files for inputs, first convert them to a geoprocessing raster layer.

Required inputs:

DEM (https://apps.nationalmap.gov/downloader/#/)
    
LANDFIRE Anderson13 fuel model (https://www.landfire.gov/viewer/)
    
Ignition points (feature class)

Optional inputs:
    Barrier features (feature class)

References:
1. Alexander, M., & Cruz, M. (2019). A rule of thumb for estimating a wildfires’s forward spread rate.
2. Anderson, H. E. (1982). Aids to determining fuel models for estimating fire behavior (INT-GTR-122; p. INT-GTR-122). U.S. Department of Agriculture, Forest Service, Intermountain Forest and Range Experiment Station. https://doi.org/10.2737/INT-GTR-122
3. Andrews, P. L. (2018). The Rothermel surface fire spread model and associated developments: A comprehensive explanation (RMRS-GTR-371; p. RMRS-GTR-371). U.S. Department of Agriculture, Forest Service, Rocky Mountain Research Station. https://doi.org/10.2737/RMRS-GTR-371
4. Baranovskiy, N. V., & Kirienko, V. A. (2022). Forest Fuel Drying, Pyrolysis and Ignition Processes during Forest Fire: A Review. Processes, 10(1). https://doi.org/10.3390/pr10010089
5. Brian L Tolk (CTR), Inga P La Puma, Daryn J Dockter (CTR), Charley M Martin, Paul F Bourget (CTR), Sean D Beverly, Eva L Soluk, Deborah Lissfelt (CTR), Sofronio C Propios (CTR), Lucas J Porter (CTR), Erica J Degaga, Tobin Smail (CTR), & Jacob G Casey (CTR). (n.d.). LANDFIRE 2022 (230) Update [Dataset]. U.S. Geological Survey. https://doi.org/10.5066/P974JF8W
6. Grishin, A. M., Zima, V. P., Kuznetsov, V. T., & Skorik, A. I. (2002). Ignition of Combustible Forest Materials by a Radiant Energy Flux. Combustion, Explosion and Shock Waves, 38(1), 24–29. https://doi.org/10.1023/A:1014097631884
7. McAllister, S., Grenfell, I., Hadlow, A., Jolly, W. M., Finney, M., & Cohen, J. (2012). Piloted ignition of live forest fuels. Fire Safety Journal. 51: 133-142., 133–142. https://doi.org/10.1016/j.firesaf.2012.04.001
8. Mindykowski, P., Fuentes, A., Consalvi, J. L., & Porterie, B. (2011). Piloted ignition of wildland fuels. Fire Safety Journal, Forest Fires, 46(1), 34–40. https://doi.org/10.1016/j.firesaf.2010.09.003
9. Xu, H., Zlatanova, S., Liang, R., & Canbulat, I. (2025). Generative AI as a Pillar for Predicting 2D and 3D Wildfire Spread: Beyond Physics-Based Models and Traditional Deep Learning. Fire, 8(8). https://doi.org/10.3390/fire8080293
10. Xu, Y., Li, D., Ma, H., Lin, R., & Zhang, F. (2022). Modeling Forest Fire Spread Using Machine Learning-Based Cellular Automata in a GIS Environment. Forests, 13(12). https://doi.org/10.3390/f13121974




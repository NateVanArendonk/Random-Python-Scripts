# Convert mask rasters to polygon extents
# N. VanArendonk, S. C. Crosby

# Helpful link, https://anitagraser.com/2019/03/03/stand-alone-pyqgis-scripts-with-osgeo4w/

# Packages
from qgis.core import *
from qgis.gui import *
from qgis_fxns import *
import os

# USER Specific cocations of processessing and python libraries - MUST BE CHANGED FOR LOCAL PATHS
processPath = 'C:\\Program Files\\QGIS 3.16\\apps\\qgis-ltr\\python\\plugins\\processing\\'
scriptPath = 'C:\\Program Files\\QGIS 3.16\\apps\\Python37\\Scripts\\'

# Initialize QGIS & Toolboxes
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Add paths to necessary libraries
sys.path.append(processPath)
sys.path.append(scriptPath)

# Add the processing toolbox
from processing.core.Processing import Processing
Processing.initialize()

# What is this? Not sure but we need it - This mostly gives meta on the processing step....might be able to remove 
feedback = QgsProcessingFeedback()

# Set these paths:
netFol = 'g:\\pscomos\\tier3\\model_20210708\\whatcom\\run_20210817\\_post_processed\\floodtype\\' # Input rasters
datOutFol = 'g:\\pscomos\\tier3\\model_20210708\\whatcom\\run_20210817\\_post_processed\\final_shapefile\\' # Output shapefiles
junkFol = 'g:\\pscomos\\tier3\\model_20210708\\whatcom\\run_20210817\\_post_processed\\junk\\'

# Get list of all netcdf files now
all_files = [f for f in listdir(netFol) if isfile(join(netFol, f))]  # Finds all files
netcdf_files = [f for f in all_files if f.endswith('.nc')]  # Finds all netcdf files

# Clean out junk folder
cleanup_folder(junkFol)

# Uncomment to test single file
# netcdf_files = [netcdf_files[0]]

# Loop over rasters
for ncf in netcdf_files:
    # Merge tiles and make a single raster ( There is no merging here?)
    vName = ncf.replace('_best-guess.nc','.tiff') # Name to be passed to function
    fullNetName = netFol + ncf # Full path to file
    fullRasName = datOutFol + vName # Full path to output

    # Options for the Raster merging - use as many/little as we want
    EPSG        = 'EPSG:6339' # Defines SRS for dataset
    options     = gdal.BuildVRTOptions(outputSRS=EPSG)

    # Convert from nc to tiff store in intermediate junk folder
    mrgRast     = merge_netcdf_no_tiles(fullNetName, datOutFol, vName, options)
    print('\n')
    print('netCDF %s successfully loaded, merged and saved in %s\n' % (fullNetName,datOutFol))

    # Name of shape file to output
    pName = ncf.replace('_best-guess.nc', '_poly.shp')

    # Converts mask raster to polygon with labels for 1 and 2 (conn/disconn) and stores in junk folder
    polygonize_raster(datOutFol, junkFol, vName, pName)

    # Filter Polygons for connected (DN=1) and disconnected (DN=2).  This DN code is automatic somehow (in matlab we have 1 for flood, 2 for disconnected)
    #     This takes polygon with multiple shape/flood types (1,2) and makes individual files
    fullPolygonPath = junkFol + pName # Location of polygon file
    ext1 = ncf.replace('_best-guess.nc','_connected.shp')
    ext2 = ncf.replace('_best-guess.nc','_disconnected.shp')
    extOut1 = junkFol + ext1 # Name of filtered data for DN = 1
    extOut2 = junkFol + ext2 # Name of filtered data for DN = 2
    exp1 = "DN = 1" # Expression for DN = 1
    exp2 = "DN = 2" # Expression for DN = 2
    filter_polygons(fullPolygonPath,extOut1,exp1,feedback,processPath,scriptPath)
    filter_polygons(fullPolygonPath,extOut2,exp2,feedback,processPath,scriptPath)

    # Fix Geometries, sometimes shape files look funny in QGIS (less so in ArcGIS) but this fixed issues
    fixed1 = datOutFol + ncf.replace('_best-guess.nc','_connected.shp')
    fixed2 = datOutFol + ncf.replace('_best-guess.nc','_disconnected.shp')
    fix_geometries(extOut1,fixed1,processPath,scriptPath)
    fix_geometries(extOut2,fixed2,processPath,scriptPath)

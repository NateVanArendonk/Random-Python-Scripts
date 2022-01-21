# Code to load in rasters from netcdf or tiff
from os import listdir
from os.path import isfile,join
import qgis.utils
from qgis.core import QgsRasterLayer
from PyQt5.QtCore import QFileInfo
from qgis.core import *
from qgis.gui import *
import numpy as np
import math
from typing import List
import time


# Function to load in a netcdf to raster from file path and crs
def LoadVectorFromString(vector,crsCode,colorMap,alpha,group):

    # Get meta on the file
    fileInfo = QFileInfo(vector)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    # Initialize a raster layer object
    layer = QgsVectorLayer(path, baseName)
    layer.setOpacity(alpha)

    # Set the CRS
    crs = layer.crs()
    crs.createFromId(crsCode)
    layer.setCrs(crs)

    # Load the data into Q GUI
    if layer.isValid() is True:
        # Add Layer to Workspace
        QgsProject.instance().addMapLayer(layer,False) # set to false to define position of layer
        group.addLayer(layer) # Add layer to desired group

        single_symbol_renderer = layer.renderer()
        symbol = single_symbol_renderer.symbol()
        #Set fill colour
        symbol.setColor(QColor.fromRgb(colorMap[0],colorMap[1],colorMap[2]))
        #Refresh
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())

        txt = "Layer " + baseName + " Successfully Added"
        print(txt)
        print('')
    else:
        txt = 'Unable to load ' + baseName + ' ...Please confirm path is correct'
        print(txt)
        print(path)
        print('')

checkSpeed = 0
if checkSpeed:
    t = time.time()

# 1. Get list of file names
datOutFol = 'g:\\pscomos\\tier3\\model_20210708\\whatcom\\run_20210817\\_post_processed\\final_shapefile\\'
# Get list of all of the RPs and SLR scenarios
slrVals   = [0, 25, 50, 100, 150, 200, 300, 500]
rpVals    = [0, 1, 5, 10, 20, 50, 100, 'King']
FTVals    = ['', '_disconnected']
slrVals   = [slrVals[0]]
# rpVals    = [rpVals[0]]

# Define Color and Alpha parameters and CRS
color1 = [49, 130, 189] # Dark Blue
color2 = [158, 202, 225] # Lighter Blue
alpha = 0.5 # transparency
crs = 6339

# Loop and load
# ct = 1
for jj in rpVals:
    # Make group name
    #groupName   = slr + '_' + rp    
    if jj == 'King':
        rp = 'RPKing'
    else:
        rp = f"RP{jj:04}" # convert to string of correct format for recurrence interval
    
    groupName   = rp
    root = QgsProject.instance().layerTreeRoot()
    currentGroup = root.addGroup(groupName)    
    
    for ii in slrVals:    
        slr         = f"SLR{ii:03}"
        # Make file names for both flood types
        fileName1   = 'floodtype_' + slr + '_' + rp + FTVals[0] + '.shp'
        fileName2   = 'floodtype_' + slr + '_' + rp + FTVals[1] + '.shp'
        fileName1   = datOutFol + fileName1
        fileName2   = datOutFol + fileName2

        # Load data
        LoadVectorFromString(fileName1,crs,color1,alpha,currentGroup)
        LoadVectorFromString(fileName2,crs,color2,alpha,currentGroup)
        # vlayer = iface.addVectorLayer(fileName1, "test", "ogr")


# Now group based on SLR Scenarios - Needs work
# root = QgsProject.instance().layerTreeRoot()
# for ii in slrVals:
#     slr          = f"SLR{ii:03}"
#     newGroupName = slr
#     ng1 = root.insertGroup(0, newGroupName)
#     for jj in rpVals:
#         if jj == 'King':
#             rp = 'RPKing'
#         else:
#             rp = f"RP{jj:04}" # convert to string of correct format for recurrence interval        slr         = f"SLR{ii:03}"
#
#     ogGroup = slr + '_' + rp
#     ng1.addGroup(ogGroup)
#     root.addChildNode(ogGroup)

if checkSpeed:
    elapsed = time.time() - t
    print("%.2f seconds elapsed" % (elapsed))

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

checkSpeed = 1
if checkSpeed:
    t = time.time()

# Get list of file names
datOutFol = 'F:\\model\\cosmos\\cosmos_qaqc\\tulalip_02222022\\Outputs_20220220\\final_shapefile\\'
# Get list of all of the RPs and SLR scenarios
slrVals   = [0, 50, 75, 100, 150, 200, 250, 300, 350, 450, 500, 550]
rpVals    = [0, 1, 5, 10, 20, 50, 100]
FTVals    = ['_connected', '_disconnected']

# Plotting Params 
color1 = [49, 130, 189] # Dark Blue
color2 = [158, 202, 225] # Lighter Blue
alpha = 0.5 # transparency
crs = 6339

root = QgsProject.instance().layerTreeRoot() # Might be able to place it outside of loop 
for ii in slrVals:
    # Get root of groups in project 
    slr         = f"SLR{ii:03}"
    slr_group = root.addGroup(slr) # make a SLR parent group 
    for jj in rpVals:
        if jj == 'King':
            rp = 'RPKing'
        else:
            rp = f"RP{jj:04}" # convert to string of correct format for recurrence interval
        
        groupName = slr + "_" + rp
        currentGroup = root.addGroup(groupName)  
        
        # Make file names for both flood types
        fileName1   = 'floodtype_' + slr + '_' + rp + FTVals[0] + '.shp'
        fileName2   = 'floodtype_' + slr + '_' + rp + FTVals[1] + '.shp'
        fileName1   = datOutFol + fileName1
        fileName2   = datOutFol + fileName2

        # Load data
        LoadVectorFromString(fileName1,crs,color1,alpha,currentGroup)
        LoadVectorFromString(fileName2,crs,color2,alpha,currentGroup)
        
        # Find groups to add 
        layer = root.findGroup(groupName) # Find shapefile data
        slr_group = root.findGroup(slr) # Find SLR parent group 
        
        # Add to Parent Group 
        clone = layer.clone()
        parent = layer.parent()
        slr_group.insertChildNode(0, clone) # Insert data into parent group 
        parent.removeChildNode(layer) # Delete dup 

if checkSpeed:
    elapsed = time.time() - t
    print("%.2f seconds elapsed" % (elapsed))

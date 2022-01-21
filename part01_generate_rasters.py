from os.path import isfile,join
import numpy as np
import math
from typing import List
import time
import os
from pathlib import Path
from osgeo import gdal, ogr, osr
from PyQt5.QtCore import QFileInfo
import sys
import qgis.utils
from qgis.core import *
from qgis.gui import *
from qgis_fxns import *
from qgis.analysis import QgsNativeAlgorithms
# https://anitagraser.com/2019/03/03/stand-alone-pyqgis-scripts-with-osgeo4w/ Helpful link


##################### Initialize QGIS & Toolboxes ##############################
# Locations of processessing and python libraries - MUST BE CHANGED FOR LOCAL PATHS!
processPath = 'C:\\Program Files\\QGIS 3.16\\apps\\qgis-ltr\\python\\plugins\\processing\\'
scriptPath = 'C:\\Program Files\\QGIS 3.16\\apps\\Python37\\Scripts\\'

#  Initialize QGIS (Tricky setup here, don't mess with!)
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()
#  Add paths to necessary libraries
sys.path.append(processPath)
sys.path.append(scriptPath)
# initialize_processing(processPath,scriptPath) # Works better when you initialize processing module inside each fxn
#  Add the processing toolbox
import processing
from processing.core.Processing import Processing
Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms()) # Unsure if this is needed
feedback = QgsProcessingFeedback()


#*******************************************************************************
##################### Meta on Runs #############################################
#*******************************************************************************
# Folder of all the netcdf files - MUST HAVE r in front of it!!!!!!, now we can just copy and paste the extension from file explorer
netFol = r'g:\pscomos\tier3\model_20210708\whatcom\run_20210817\_post_processed\sfincs_output_tiles'
# Folder to house the merged netcdf files
datOutFol = r'g:\pscomos\tier3\model_20210708\whatcom\run_20210817\_post_processed\final_merged_rasters'

# Get list of all of the RPs and SLR scenarios
slrVals = [0, 25, 50, 100, 150, 200, 300, 500]
rpVals = [0, 1, 5, 10, 20, 50, 100, 'King']
dataTypes = ['duration', 'velocity', 'waterdepth', 'waterlevel']

# Get total number of files to process
l1 = len(slrVals)
l2 = len(rpVals)
l3 = len(dataTypes)
lenTotal = l1*l2*l3

#slrVals = [slrVals[7]] # For testing
#rpVals = [rpVals[7]]
#dataTypes = [dataTypes[2]]

# While loop
again = True
# Counter
ct = 1
while again:
    for dd in dataTypes:
        for ss in slrVals:
            for rr in rpVals:
                if rr == 'King':
                    rp = 'RPKing'
                else:
                    rp = f"RP{rr:04}

                #*******************************************************************************
                ##################### Merge tiles and make a single raster #####################
                #*******************************************************************************
                # Options for the Raster merging - use as many/little as we want
                EPSG = 'EPSG:6339'  # Defines SRS for dataset
                options = gdal.BuildVRTOptions(outputSRS=EPSG)
                slr = f"SLR{ss:03}"

                # Check existence of file
                fileName = 'merged_' + dd + '_' + rp + '_' + slr + '.tiff'
                filePath = datOutFol + fileName
                if not exists(filePath):

                    # # Execute Merge netCDF
                    merge_netcdf(netFol, datOutFol, dd, slr, rp, options)
                    print('\n')
                    print('netCDF successfully loaded, merged and saved. Number %d\n' % ct)
                    ct += 1
                    # ct = 500

    totalRan = ct
    if totalRan >= lenTotal:
        again = False















# EOF #

# #*******************************************************************************
# ##################### Polygonize Raster ########################################
# #*******************************************************************************
# # Location where the raster from previous step is located
# rasterPath = rasOutFol
# # Location to put the shapefiles that get made
# polygonPath = 'C:\\Users\\nvanarendonk\\conda_envs\\cosmos\\python_qgis_tool_cosmos_qaqc\\poly_out\\'
# # Raster name
# rasterName = 'merged_' + data2grab + '.tiff'
# # Name of shape file to output
# polygonName = data2grab + '_RP' + RP + '_SLR' + slr + '_poly.shp'
#
# # Execute polygonization of raster
# polygonize_raster(rasterPath,polygonPath,mrgRast,polygonName)


# #*******************************************************************************
# ##################### Filter Polygons for DN=1 & DN=2 ##########################
# #*******************************************************************************
# fullPolygonPath = polygonPath + polygonName # Location of polygon file
# ext1 = data2grab + '_RP' + RP + '_SLR' + slr + '_ext1.shp'
# ext2 = data2grab + '_RP' + RP + '_SLR' + slr + '_ext2.shp'
# extOut1 = polygonPath + ext1 # Name of filtered data for DN = 1
# extOut2 = polygonPath + ext2 # Name of filtered data for DN = 2
# exp1 = "DN = 1" # Expression for DN = 1
# exp2 = "DN = 2" # Expression for DN = 2
#
# # Execute filtering of data, saving shapefile to extOut file
# filter_polygons(fullPolygonPath,extOut1,exp1,feedback,processPath,scriptPath)
# filter_polygons(fullPolygonPath,extOut2,exp2,feedback,processPath,scriptPath)


# #*******************************************************************************
# ##################### Fix Geometries ###########################################
# #*******************************************************************************
# fixed1 = extOut1.replace('ext','gfix')
# fixed2 = extOut2.replace('ext','gfix')
# # fix_geometries(extOut1,fixed1,processPath,scriptPath)
# # fix_geometries(extOut2,fixed2,processPath,scriptPath)

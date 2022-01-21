from os import listdir
from os.path import isfile, join
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


# from qgis_fxns import *

# Initialize Processing toolbox qgis - Not sure if will use this
def initialize_processing(processingPath, scriptPath):
    # Add paths to necessary libraries
    sys.path.append(processingPath)
    sys.path.append(scriptPath)

    # Add the processing toolbox
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()


# Get list of netCDF names and create a virtual raster
def merge_netcdf(nfol, ofol, filename_start, slr, rp, vrtOptions):
    all_files = [f for f in listdir(nfol) if isfile(join(nfol, f))]  # Finds all files
    needed_files = [f for f in all_files if f.startswith(filename_start)]  # Finds all files that start with data type
    needed_files = [f for f in needed_files if f.endswith('.nc')]  # Finds all netcdf files
    needed_files = [f for f in needed_files if f.find(rp) != -1]  # Finds all netcdf files with RP of interest
    needed_files = [f for f in needed_files if f.find(slr) != -1]  # Finds all of the SLR files we want
    fil_ful = list()
    vrt_name = 'merged_' + filename_start + '_' + rp + '_' + slr + '.tiff'
    for f in needed_files:
        fil_ful.append(os.path.join(nfol, f))
    vrt = gdal.BuildVRT('temp.vrt', fil_ful, options=vrtOptions)
    result = os.path.join(ofol, vrt_name)
    topts = gdal.TranslateOptions(creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'])
    gdal.Translate(result, vrt, format='GTiff', options=topts)  # Saves out the VRT as a merged/mosaic'd raster
#   https://gdal.org/python/osgeo.gdal-module.html#BuildVRT buildVRT options
#   Example: options=gdal.BuildVRTOptions(outputSRS=srs_wkt, resampleAlg=gdal.GRA_Bilinear, srcNodata=-99, VRTNodata=-99)
#   Create a BuildVRTOptions() object that can be passed to gdal.BuildVRT()
#   Keyword arguments are :
#   options --- can be be an array of strings, a string or let empty and filled from other keywords..
#   resolution --- 'highest', 'lowest', 'average', 'user'.
#   outputBounds --- output bounds as (minX, minY, maxX, maxY) in target SRS.
#   xRes, yRes --- output resolution in target SRS.
#   targetAlignedPixels --- whether to force output bounds to be multiple of output resolution.
#   separate --- whether each source file goes into a separate stacked band in the VRT band.
#   bandList --- array of band numbers (index start at 1).
#   addAlpha --- whether to add an alpha mask band to the VRT when the source raster have none.
#   resampleAlg --- resampling mode.
#   outputSRS --- assigned output SRS.
#   allowProjectionDifference --- whether to accept input datasets have not the same projection. Note: they will *not* be reprojected.
#   srcNodata --- source nodata value(s).
#   VRTNodata --- nodata values at the VRT band level.
#   hideNodata --- whether to make the VRT band not report the NoData value.
#   callback --- callback method.
#   callback_data --- user data for callback.


# Converts nc raster to tiff raster
def merge_netcdf_no_tiles(npath, ofol, vrt_name, vrtOptions):
    vrt = gdal.BuildVRT('temp.vrt', npath, options=vrtOptions)
    result = os.path.join(ofol, vrt_name)
    topts = gdal.TranslateOptions(creationOptions=['COMPRESS=LZW', 'PREDICTOR=2'])
    gdal.Translate(result, vrt, format='GTiff', options=topts)  # Saves out the VRT as a merged/mosaic'd raster


# 2. Convert Polygon to a raster - BROKEN DO NOT USE
# def polygonize_raster(fullRasterPath,fullPolyOutPath):
#     polygonize_dict = { 'BAND' : 1, 'EIGHT_CONNECTEDNESS' : False, 'EXTRA' : '', 'FIELD' : 'DN', 'INPUT' : fullRasterPath, 'OUTPUT' : fullPolyOutPath }
#     processing.run('gdal:polygonize', polygonize_dict)


# Filter polygon for DN = 1 and DN = 2
def filter_polygons(polygonPath, outName, expression, feedback, processPath, scriptPath):
    # Add the processing toolbox
    sys.path.append(processPath)
    sys.path.append(scriptPath)
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    extract = \
    processing.run('native:extractbyexpression', {'INPUT': polygonPath, 'EXPRESSION': expression, 'OUTPUT': outName},
                   feedback=feedback)['OUTPUT']
    state = '%s extracted from %s' % (expression, polygonPath)
    print(state)
    print('\n')


# Save out vectors to shape file
def save_vector_to_esri_shapefile(layer, fullShapeOut):
    QgsVectorFileWriter.writeAsVectorFormat(layer, fullShapeOut, "UTF-8", layer.crs(), "ESRI Shapefile")


# Convert Polygon to raster
def polygonize_raster(rasterPath, polygonPath, rasterName, polygonName):
    # Make full path strings - Do not change
    rasterPath = rasterPath + rasterName
    rasterPath = '"%s"' % (rasterPath)
    polygonPath = polygonPath + polygonName
    polygonPath = '"%s"' % (polygonPath)

    esriCmd = '"ESRI Shapefile"'
    # Generate the command
    command = "python gdal_polygonize.py %s -f %s %s" % (rasterPath, esriCmd, polygonPath)

    # Run the command
    os.system(command)
    print('Polygonization Successful\n')


# Fix any geometries in polygon
def fix_geometries(polygonPath, outPath, processPath, scriptPath):
    # Add the processing toolbox
    sys.path.append(processPath)
    sys.path.append(scriptPath)
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    fixed = processing.run("native:fixgeometries", {'INPUT': polygonPath, 'OUTPUT': outPath})['OUTPUT']
    print('Fixed geometries and exported as %s' % (outPath))
    print('\n')


# Load Raster
def StringToRaster(raster):
    # Check if string is provided
    if isinstance(raster, basestring):
        fileInfo = QFileInfo(raster)
        baseName = fileInfo.baseName()
        path = fileInfo.filePath()
        if (baseName and path):
            raster = QgsRasterLayer(path, baseName)
            if not raster.isValid():
                print("Layer failed to load!")
                return
        else:
            print("Unable to read basename and file path - Your string is probably invalid")
            return
    return raster


# Load Vector
def StringToVector(vector):
    # Check if string is provided
    if isinstance(vector, basestring):
        fileInfo = QFileInfo(vector)
        baseName = fileInfo.baseName()
        path = fileInfo.filePath()
        if (baseName and path):
            vector = QgsVectorLayer(path, baseName)
            if not vector.isValid():
                print("Layer failed to load!")
                return
        else:
            print("Unable to read basename and file path - Your string is probably invalid")
            return
    return vector


# Delete all contents of folder     
def cleanup_folder(folderPath):
    for f in os.listdir(folderPath):
        os.remove(os.path.join(folderPath, f))

    # Add double backslashes to folder path


def add_double_backslashes(folderPath):
    folderPath = folderPath.replace('\\', '\\\\') + '\\\\'
    return folderPath

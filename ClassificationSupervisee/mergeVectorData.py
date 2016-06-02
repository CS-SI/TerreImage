# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                              -------------------
        begin               : 2016-06-02
        copyright           : (C) 2016 by CNES
        email               : alexia.mondot@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# import system libraries
import argparse
import glob
import os
import sys
import shutil

from TerreImage.terre_image_gdal_api import get_image_epsg_code_with_gdal, get_vector_epsg_with_ogr

# import logging for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('cropVectorDataToImage')
logger.setLevel(logging.DEBUG)


# TODO argparse


def mergeVectorDataFiles(listOfVectorData, outputDirectory):
    outputFilename = os.path.join(outputDirectory, "merged_vectordata.shp")
    while os.path.isfile(outputFilename):
        outputFilename = outputFilename[:-4] + "_" + outputFilename[-4:]









# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin               : 2013-11-21
        copyright           : (C) 2014 by CNES
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
import os
import shutil

from osgeo import gdal

import terre_image_run_process

# import GDAL and QGIS libraries
from osgeo import gdal, osr, ogr
gdal.UseExceptions()
import gdalconst

# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_OTBApplications')
logger.setLevel(logging.INFO)

currentOs = os.name
if currentOs == "posix":
    prefix = ""
else:
    prefix = os.path.join(os.path.dirname(__file__), "win32", "bin")


def bandmath_cli(images, expression, output_filename):
    """
    This function applies otbcli_BandMath to image with the given expression

    Keyword arguments:
        image               --    raster layer to process
        expression          --    expression to apply
        outputDirectory     --    working directory
        keyword             --    keyword for output file name
    """

    command = os.path.join(prefix, "otbcli ")
    command += " BandMath "

    args = " -il "
    for image in images:
        args += "\"" + image + "\"" + " "

    args += " -exp " + str(expression)
    args += " -out " + "\"" + output_filename + "\""

    logger.info("command: " + command)
    if os.name == "posix":
        command += args
        terre_image_run_process.run_process(command)
    else:
        terre_image_run_process.run_otb_app("BandMath", args)


def concatenateImages_cli(listImagesIn, outputname, options=None):
    """
    Runs the ConcatenateImages OTB application.

    Keyword arguments:
        listImagesIn     --    list of images to concatenates
        outputname     --    output image
    """

    if listImagesIn and outputname:
        command = os.path.join(prefix, "otbcli ")
        command += " ConcatenateImages "
        args = " -il " + " ".join(["\"" + f + "\"" for f in listImagesIn])
        args += " -out " + "\"" + outputname + "\""
        if options:
            args += " uint16 "

        logger.info("command: " + command)
        # os.system( command )
        # terre_image_utils.run_process(command)
        if os.name == "posix":
            # os.system( command )
            command += args
            terre_image_run_process.run_process(command)
        else:
            terre_image_run_process.run_otb_app("ConcatenateImages", args)


def kmeans_cli(image, nbClass, outputDirectory):
    """
    Runs the KMeansClassification OTB application.

    Args:
        image:
        nbClass:
        outputDirectory:

    Returns:

    """
    filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0])
    output = os.path.join(outputDirectory, filenameWithoutExtension + "_kmeans_" + str(nbClass) + ".tif")
    if not os.path.isfile(output):
        if image and nbClass and outputDirectory:
            command = os.path.join(prefix, "otbcli")
            command += " KMeansClassification "
            args = " -in " + "\"" + image + "\""
            args += " -out " + "\"" + output + "\""
            args += " -nc " + str(nbClass)
            args += " -rand " + str(42)

            logger.info("command: " + command)

            if os.name == "posix":
                command += args
                terre_image_run_process.run_process(command)
            else:
                terre_image_run_process.run_otb_app("KMeansClassification", args)
    return output


def color_mapping_cli_ref_image(image_to_color, reference_image, working_dir):
    """
    Runs the ColorMapping OTB application.

    Args:
        image_to_color:
        reference_image:
        working_dir:

    Returns:

    """
    output_filename = os.path.join(working_dir, os.path.splitext(os.path.basename(image_to_color))[0]) + "colored.tif"

    if not os.path.isfile(output_filename):
        logger.info(output_filename)
        command = os.path.join(prefix, "otbcli")
        command += " ColorMapping "
        args = " -in " + "\"" + image_to_color + "\""
        args += " -out " + "\"" + output_filename + "\" uint8"
        args += " -method \"image\""
        args += " -method.image.in " + "\"" + reference_image + "\""
        logger.info("command: " + command)

        if os.name == "posix":
            command += args
            terre_image_run_process.run_process(command)
        else:
            terre_image_run_process.run_otb_app("ColorMapping", args)

    return output_filename


def otbcli_export_kmz(filename, working_directory):
    """
    Runs the KmzExport OTB application.

    Args:
        filename:
        working_directory:

    Returns:

    """
    output_kmz = os.path.join(working_directory, os.path.basename(os.path.splitext(filename)[0]) + ".kmz")
    if not os.path.isfile(output_kmz):
        command = os.path.join(prefix, "otbcli ")
        command += "KmzExport "
        args = " -in " + "\"" + filename + "\""
        args += " -out " + "\"" + output_kmz + "\""

        logger.info("command: " + command)
        terre_image_run_process.run_process(command)
        if os.name == "posix":
            command += args
            terre_image_run_process.run_process(command)
        else:
            terre_image_run_process.run_otb_app("KmzExport", args)

    output_kmz = os.path.join(working_directory, os.path.basename(os.path.splitext(filename)[0]) + "xt.kmz")
    return output_kmz



def compute_overviews(filename):
    """
    Runs gdaladdo on the given filename

    Args:
        filename:

    Returns:

    """
    if not os.path.isfile(filename + ".ovr"):
        command = "gdaladdo "
        command += " -ro "
        command += "\"" + filename + "\""
        command += " 2 4 8 16"
        logger.debug("command to run" + command)
        terre_image_run_process.run_process(command)



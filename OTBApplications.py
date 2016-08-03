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

from terre_image_run_process import TerreImageProcess, get_otb_command

# import GDAL and QGIS libraries
from osgeo import gdal, osr, ogr
gdal.UseExceptions()
import gdalconst

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()

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

    args = " -il "
    for image in images:
        args += u'"{}" '.format(image)

    args += u'-exp {} -out "{}"' .format(expression, output_filename)

    command = get_otb_command("BandMath", args)
    logger.info("command: " + command)
    TerreImageProcess().run_process(command)


def concatenateImages_cli(listImagesIn, outputname, options=None):
    """
    Runs the ConcatenateImages OTB application.

    Keyword arguments:
        listImagesIn     --    list of images to concatenates
        outputname     --    output image
    """

    if listImagesIn and outputname:
        args = u' -il {}'.format(" ".join(["\"" + f + "\"" for f in listImagesIn]))
        args += u' -out "{}"'.format(outputname)
        if options:
            args += u" uint16 "

        command = get_otb_command("ConcatenateImages", args)
        logger.info("command: " + command)
        TerreImageProcess().run_process(command)


def kmeans_cli(image, nbClass, outputDirectory):
    """
    pass
    """
    terre_image_logging.display_parameters(locals(), "kmeans_cli", logger)
    filenameWithoutExtension = os.path.basename(os.path.splitext(image)[0])
    output = os.path.join(outputDirectory, u"{}_kmeans_{}.tif".format(filenameWithoutExtension, nbClass))  # + temp[index:]
    if not os.path.isfile(output):
        if image and nbClass and outputDirectory:
            args = u' -in "{}" -out "{}" -nc {} -rand {} '.format(image,
                                                                  output,
                                                                  nbClass,
                                                                  42)
            command = get_otb_command("KMeansClassification", args)
            logger.info("command: " + command)
            TerreImageProcess().run_process(command)
    return output


def color_mapping_cli_ref_image(image_to_color, reference_image, working_dir):
    terre_image_logging.display_parameters(locals(), "color_mapping_cli_ref_image", logger)
    output_filename = os.path.join(working_dir, os.path.splitext(os.path.basename(image_to_color))[0] + "colored.tif")

    if not os.path.isfile(output_filename):
        logger.info(output_filename)
        command = os.path.join(prefix, "otbcli")
        command += " ColorMapping "
        args = u' -in "{}" -out "{}" uint8 -method "image" -method.image.in "{}" '.format(image_to_color,
                                                                                    output_filename,
                                                                                    reference_image)
        command = get_otb_command("ColorMapping", args)
        logger.info("command: " + command)
        TerreImageProcess().run_process(command)
    return output_filename


def otbcli_export_kmz(filename, working_directory):
    output_kmz = os.path.join(working_directory, os.path.basename(os.path.splitext(filename)[0]) + ".kmz")
    if not os.path.isfile(output_kmz):
        args = u' -in "{}" -out "{}"'.format(filename, output_kmz)

        command = get_otb_command("KmzExport", args)
        logger.info("command: " + command)
        TerreImageProcess().run_process(command)
        output_kmz = os.path.join(working_directory, os.path.basename(os.path.splitext(filename)[0]) + "xt.kmz")
        return output_kmz


def read_image_info_cli(image_in):
    """
    Returns the output of OTB Application ReadImageInfo
    Args:
        image_in:

    Returns:

    """

    args = u" -in %s"%(unicode(image_in))
    command = get_otb_command("ReadImageInfo", args)
    result = TerreImageProcess().run_process(command)
    return result



def compute_statistics_cli(image_in, xml_output):
    """
    Returns the output of OTB Application ComputeImagesStatistics
    Args:
        image_in:

    Returns:

    """

    args = u" -il {} -out {}".format(image_in, xml_output)
    command = get_otb_command("ComputeImagesStatistics", args)
    result = TerreImageProcess().run_process(command)
    return result


def train_image_classifier_cli(vrtfile, vd, outstatfile, outsvmfile, confmat):
    """
    Returns the output of OTB Application TrainImagesClassifier
    Args:
        image_in:

    Returns:

    """
    args = u" -io.il {} -io.vd {} -io.imstat {} -io.out {}" \
           u" -io.confmatout {} -classifier libsvm -sample.vtr 0.1".format(vrtfile,
                                                           vd,
                                                           outstatfile,
                                                           outsvmfile,
                                                           confmat)
    command = get_otb_command("TrainImagesClassifier", args)
    result = TerreImageProcess().run_process(command)
    return result


def image_classifier_cli(vrtfile, outstatfile, outsvmfile, out):
    """
    Returns the output of OTB Application ImageClassifier
    Args:
        image_in:

    Returns:

    """

    args = u"-in {} -imstat {} -model {} -out {}".format(vrtfile, outstatfile, outsvmfile, out)
    command = get_otb_command("ImageClassifier", args)
    result = TerreImageProcess().run_process(command)
    return result


def classification_map_regularization_cli(out, outregul):
    """
    Returns the output of OTB Application ClassificationMapRegularization
    Args:
        image_in:

    Returns:

    """

    args = u"-io.in {} -io.out {} -ip.radius 1 -ip.suvbool false".format(out, outregul)
    command = get_otb_command("ClassificationMapRegularization", args)
    result = TerreImageProcess().run_process(command)
    return result


def ComputeLabelImagePopulation_cli(im1, im2, out):
    """

    Args:
        im1:
        im2:

    Returns:

    """
    args = u"-in1 {} -in2 {} -out {}".format(im1, im2, out)
    command = get_otb_command("ComputeLabelImagePopulation", args)
    result = TerreImageProcess().run_process(command)
    return result


def ImageEnvelope_cli(image_in, vector_out, epsg_code=""):
    """

    Args:
        im1:
        im2:

    Returns:

    """
    args = u"-in {} -out {}".format(image_in, vector_out)
    if epsg_code:
        args += u' -proj "{}"'.format(epsg_code)
    command = get_otb_command("ImageEnvelope", args)
    result = TerreImageProcess().run_process(command)
    return result
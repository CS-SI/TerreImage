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

import os
from terre_image_run_process import TerreImageProcess

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()

def unionPolygonsWithOGR(filenames, outputDirectory):
    """
    Build up the union of all the geometries of the given masks.

    Keyword arguments:
        filenames -- list of masks filenames
    """
    outputFilename = os.path.join(outputDirectory, "vectorMerged.shp")
    indexClass=0
    for f in filenames:
        base = os.path.basename(os.path.splitext(f)[0])
        #Add class
        command = u'ogrinfo {} -sql "ALTER TABLE {} ADD COLUMN Class numeric(15)"'.format(f, base)
        TerreImageProcess().run_process(command)
        command = u'ogrinfo {} -dialect SQLite -sql "UPDATE {} SET Class = {}"'.format(f, base, indexClass)
        TerreImageProcess().run_process(command)
        #Add Label
        command = u'ogrinfo {} -sql "ALTER TABLE {} ADD COLUMN Label character(15)"'.format(f, base)
        TerreImageProcess().run_process(command)
        command = u'ogrinfo {} -dialect SQLite -sql "UPDATE {} SET Label = \'{}\'"'.format(f, base, base)
        TerreImageProcess().run_process(command)
        #update output
        command = u'ogr2ogr -update -append {} {}'.format(outputFilename, f)
        TerreImageProcess().run_process(command)
        indexClass+=1

    return outputFilename


def compute_overviews(filename):
    """
    Runs gdaladdo on the given filename
    """
    if not os.path.isfile(filename + ".ovr"):
        command = "gdaladdo "
        command += " -ro "
        command += "\"" + filename + "\""
        command += " 2 4 8 16"
        logger.debug("command to run" + command)
        TerreImageProcess().run_process(command)


def gdal_edit_remove_no_data(image_in):
    """
    Runs gdal_edit to remove the no data value of the given image
    Args:
        image_in:

    Returns:

    """
    command = u"gdal_edit.py -a_nodata None {}".format(image_in)
    TerreImageProcess().run_process(command)


def gdal_translate_remove_no_data(image_in, image_out):
    """
    Runs gdal_translate to remove the no data value of the given image

    Args:
        image_in:
        image_out:

    Returns:

    """
    command = u"gdal_translate -a_nodata None {} {}".format(image_in, image_out)
    TerreImageProcess().run_process(command)

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

# import GDAL and QGIS libraries
from osgeo import gdal, osr, ogr
gdal.UseExceptions()
import gdalconst

# import logging for debug messages
import terre_image_logging
logger = terre_image_logging.configure_logger()


def get_image_epsg_code_with_gdal(image_in):
    """
    Extract the following information from the given image:
        - epsg code
    """
    try:
        dataset = gdal.Open(image_in, gdalconst.GA_ReadOnly)
    except RuntimeError:  # OSError is get when the access to a folder is refused
        logger.exception("Error: Opening " + image_in)
        return

    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(dataset.GetProjectionRef())
    codeEPSG = str(spatialReference.GetAttrValue("AUTHORITY", 1))
    logger.debug("EPSG: {}".format(codeEPSG))
    return codeEPSG


def get_vector_epsg_with_ogr(vector_in):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.Open(vector_in)
    layer = datasource.GetLayer()
    spref = layer.GetSpatialRef()
    epsg=layer.GetSpatialRef().GetAttrValue("AUTHORITY", 1)
    return epsg



def computeStatistics(OneFeature, i, j = None, nodata = True):
    """
    From the given feature, computes its statistics

    Keyword Arguments :
        OneFeature    --    raster layer to analyze
        i             --    only for debugging
    """

    logger.debug("one feature : " + OneFeature)

    # # saving the feature only for testing
    # out_one = OneFeature + str(i) + ".tif"
    # shutil.copy(OneFeature, out_one)
    # logger.debug(out_one)
    # /testing

    dataset = gdal.Open(OneFeature, gdal.GA_ReadOnly)
    # dataset  : GDALDataset
    if dataset is None:
        logger.error(u"Error : Opening file {}".format(OneFeature))
    else:
        if j is None:
            band = dataset.GetRasterBand(1)
        else:
            band = dataset.GetRasterBand(j)
        if nodata:
            band.SetNoDataValue(0)
        stats = band.ComputeStatistics(False)

        logger.debug("Feature {} : {}".format(i, stats))
        return stats

    dataset = None
    return None


def get_image_size_with_gdal(image_in, get_pixel_size=False):
    """
    Extract the following information from the given image:
        - size x
        - size y
    """
    try:
        dataset = gdal.Open(image_in, gdalconst.GA_ReadOnly)
    except RuntimeError:  # OSError is get when the access to a folder is refused
        logger.exception("Error: Opening " + image_in)
        return

    size = [dataset.RasterXSize, dataset.RasterYSize]

    if get_pixel_size:
        geotransform = dataset.GetGeoTransform()
        pixel_size_x = geotransform[1]
        pixel_size_y = geotransform[5]
        pixel_size = [pixel_size_x, pixel_size_y]
        return size, pixel_size

    return size
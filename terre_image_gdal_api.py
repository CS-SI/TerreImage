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

# import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger('TerreImage_gdal_api')
logger.setLevel(logging.INFO)


def get_image_epsg_code_with_gdal(image_in):
    """
    Extract the following information from the given image:
        - epsg code
        - up left corner
        - bottom right corner
        - spacing x
        - spacing y
        - size x
        - size y
        - min of the band if asked
    """
    try:
        dataset = gdal.Open(str(image_in), gdalconst.GA_ReadOnly)
    except RuntimeError:  # OSError is get when the access to a folder is refused
        logger.exception("Error: Opening " + str(image_in))
        return

    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromWkt(dataset.GetProjectionRef())
    codeEPSG = str(spatialReference.GetAttrValue("AUTHORITY", 1))
    logger.debug("EPSG: " + str(codeEPSG))
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

    dataset = gdal.Open(str(OneFeature), gdal.GA_ReadOnly)
    # dataset  : GDALDataset
    if dataset is None:
        print "Error : Opening file ", OneFeature
    else:
        if j is None:
            band = dataset.GetRasterBand(1)
        else:
            band = dataset.GetRasterBand(j)
        if nodata:
            band.SetNoDataValue(0)
        stats = band.ComputeStatistics(False)

        logger.debug("Feature " + str(i) + " : ")
        logger.debug(stats)
        return stats

    dataset = None
    return None


def unionPolygonsWithOGR(filenames, outputDirectory):
    """
    Build up the union of all the geometries of the given masks.

    Keyword arguments:
        filenames -- list of masks filenames
    """
    outputFilename = os.path.join(outputDirectory, "vectorMerged.shp")
    print outputFilename

    # creating an empty vector layer
    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driverName )
    if drv is None:
        print "%s driver not available.\n" % driverName
        return None

    logger.debug( "outputVectorLayer" + str( outputFilename ))

    ds_out = drv.CreateDataSource( outputFilename )
    if ds_out is None:
        print "Creation of output file failed.\n"
        return None

    #end creating vector layer
    # creating a layer in the vector file
    lyr_out = ds_out.CreateLayer( "layer", None, ogr.wkbPolygon )
    if lyr_out is None:
        print "Layer creation failed.\n"
        return None

    #creating a field inside the layer
    field_class = ogr.FieldDefn( "CLASS", ogr.OFTReal )
    field_label = ogr.FieldDefn( "Label", ogr.OFTString )

    if lyr_out.CreateField ( field_class ) != 0:
        print "Creating Name field failed.\n"
        return None
    if lyr_out.CreateField ( field_label ) != 0:
        print "Creating Name field failed.\n"
        return None

    indexClass=1

    for filename in filenames:
        label = os.path.splitext(os.path.basename(filename))[0]
        print "label", label
        logging.debug("Mask filename : %s" %(filename))
        ds = ogr.Open(filename)
        if ds is None:
            msg = "It was not possible to open the file (probably an empty GML file) : %s " %(filename)
            logging.warning(msg)
            continue

        layer = ds.GetLayer()
        if layer is None:
            msg = "Error creating the layer associated to the file : %s" %()
            logging.warning(msg)
            continue

        for feature in layer:
            indexClass = feature.GetFieldIndex("CLASS")
            indexLabel = feature.GetFieldIndex("LABEL")
            feature.SetField( indexClass, indexClass )
            feature.SetField( indexLabel, label)
            lyr_out.CreateFeature(feature)
        indexClass+=1
    ds.Destroy()

    ds = layer = feature = geom = None
    print outputFilename
    return outputFilename



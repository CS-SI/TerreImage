# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerreImage
                    -------------------
        begin               : 2016-06-20
        copyright           : (C) 2016 by CNES
        email               : mickael.savinaud@c-s.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************
"""

from osgeo import gdal
import xml.etree.ElementTree as ET
import os
import argparse
import re
from TerreImage import OTBApplications
from TerreImage import terre_image_gdal_system
from TerreImage import terre_image_exceptions

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()

def create_vrt_from_filelist(filelist, vrt_name):
    logger.info("----CREATE VRT----")
    logger.debug("filelist {}".format(filelist))
    logger.debug("vrt_name {}".format(vrt_name))

    rootNode = ET.Element( 'VRTDataset' )

    for filename in filelist:
        logger.debug(filename)
        ds = gdal.Open(filename)

        logger.debug("[ RASTER BAND COUNT ]: {}".format(ds.RasterCount))
        for band_number in range( ds.RasterCount ):
            band_number += 1
            bandNode = ET.SubElement( rootNode, "VRTRasterBand", {'band': '1'} )

            sourceNode = ET.SubElement(bandNode, 'SimpleSource')
            node = ET.SubElement(sourceNode, 'SourceFilename', {'relativeToVRT': '1'})
            node.text = filename
            node = ET.SubElement(sourceNode, 'SourceBand')
            node.text = str(band_number)
        
            band = ds.GetRasterBand(band_number)
            dataType = gdal.GetDataTypeName(band.DataType)
            bandNode.attrib['dataType'] = dataType

    ds1 = gdal.Open(filelist[0])
    rootNode.attrib['rasterXSize'] = str(ds1.RasterXSize)
    rootNode.attrib['rasterYSize'] = str(ds1.RasterYSize)

    geotransform = ds.GetGeoTransform()
    ftuple = tuple(map(str, geotransform))
    geotransform = ET.SubElement( rootNode, "GeoTransform")
    geotransform.text = ", ".join(ftuple)  # "0.0, 1.0, 0.0, 0.0, 0.0, -1.0"
    node = ET.SubElement(rootNode, 'SRS')
    node.text = ds.GetProjection() # projection

    stringToReturn = ET.tostring(rootNode)
    logger.debug(stringToReturn)

    #if not os.path.isfile( vrt_name):
    writer = open( vrt_name, 'w')
    writer.write( stringToReturn )
    writer.close()


def full_classification(rasterlist, vectorlist, outputclassification, out_pop, working_directory):
    """

    Args:
        filelist:
        vd:
        out:
        outregul:
        working_directory:

    Returns:

    """
    # Merge the input images
    # logger.info("----CREATE VRT----")
    vrt_file = os.path.join(working_directory, "classif.VRT")
    create_vrt_from_filelist(rasterlist, vrt_file)
    
    #compute stats
    logger.info("----COMPUTE STATS----")
    out_stat_file = os.path.join(working_directory, "stats.xml")
    OTBApplications.compute_statistics_cli(vrt_file, out_stat_file)

    # Train images
    logger.info("----TRAIN----")
    out_rf_file = os.path.join(working_directory, "rf.model")
    conf_mat = os.path.join(working_directory, "rf.mat")
    result = OTBApplications.train_image_classifier_cli(vrt_file, vectorlist, out_stat_file, out_rf_file, conf_mat)

    kappa = None
    if result:
        # type(result_sensor) = PyQt4.QtCore.QByteArray
        for line in str(result).splitlines():
            if "Kappa" in line:
                # sensor_line = result_sensor[0]
                kappa = re.search('Kappa index: ([\d.]+)$', line)
                if kappa:
                    # group 1 parce qu'on a demande qqchose de particulier a la regexpr a cause des ()
                    try :
                        kappa = float(kappa.group(1))
                    except ValueError:
                        kappa = None
    if kappa == None:
        raise terre_image_exceptions.TerreImageClassificationError("Could not find kappa in train image classifier result")

    # Image Classification 
    logger.info("----CLASSIF----")
    out_image_classifier = os.path.join(working_directory, "out_image_classifier.TIF")
    OTBApplications.image_classifier_cli(vrt_file, out_stat_file, out_rf_file, out_image_classifier)

    # Regularization
    logger.info("----REGULARISATION----")
    out_image_classifier_with_nodata = "{}_with_no_data{}".format(os.path.splitext(outputclassification)[0],
                                                                  os.path.splitext(outputclassification)[1])
    OTBApplications.classification_map_regularization_cli(out_image_classifier, out_image_classifier_with_nodata)
    # remove no data (Bug OTB)
    terre_image_gdal_system.gdal_translate_remove_no_data(out_image_classifier_with_nodata, outputclassification)

    # Population stats
    logger.info("----POPULATION STATS----")
    OTBApplications.ComputeLabelImagePopulation_cli(outputclassification, outputclassification, out_pop)

    return conf_mat, kappa



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    #parser.add_argument('--filelist', nargs='*', type=argparse.FileType('r'))
    parser.add_argument('--filelist', nargs='*')
    parser.add_argument('--vd')
    parser.add_argument('--out')
    parser.add_argument('--outregul')
    parser.add_argument('--working_dir')
    args = parser.parse_args()

    full_classification(args.filelist,
                        args.vd,
                        args.out,
                        args.outregul,
                        args.working_dir)

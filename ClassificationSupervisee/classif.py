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

import logging
# create logger
logger = logging.getLogger( 'Classif' )
logger.setLevel(logging.INFO)

def create_vrt_from_filelist(filelist, vrt_name):
    rootNode = ET.Element( 'VRTDataset' )

    for filename in filelist:
        logging.debug(filename)
        ds = gdal.Open(filename)

        logging.debug("[ RASTER BAND COUNT ]: {}".format(ds.RasterCount))
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
    logging.debug(stringToReturn)

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
    vrt_file = os.path.join(working_directory, "classif.VRT")
    create_vrt_from_filelist(rasterlist, vrt_file)
    
    #compute stats
    logging.info("----COMPUTE STATS----")
    out_stat_file = os.path.join(working_directory, "stats.xml")
    OTBApplications.compute_statistics_cli(vrt_file, out_stat_file)

    # Train images
    logging.info("----TRAIN----")
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
                        kappa = int(kappa.group(1))
                    except ValueError:
                        kappa = None
    if not kappa:
        return

    # Image Classification 
    logging.info("----CLASSIF----")
    out = os.path.join(working_directory, "out_classifier.TIF")
    OTBApplications.image_classifier_cli(vrt_file, out_stat_file, out_rf_file, out)

    # Regularization
    logging.info("----REGULARISATION----")
    OTBApplications.classification_map_regularization_cli(out, outputclassification)

    # Population stats
    logging.info("----POPULATION STATS----")
    OTBApplications.ComputeLabelImagePopulation_cli(outputclassification, outputclassification, out)

    #TODO ajout de la sauvegarde des parameters

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

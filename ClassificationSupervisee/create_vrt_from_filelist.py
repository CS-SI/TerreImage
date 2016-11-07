

from osgeo import gdal
import xml.etree.ElementTree as ET
import os
import argparse

# import logging for debug messages
from TerreImage import terre_image_logging
logger = terre_image_logging.configure_logger()



def create_vrt_from_filelist(vrt_name, filelist):
    rootNode = ET.Element( 'VRTDataset' )

    totalXSize = 512
    totalYSize = 512

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

    rootNode.attrib['rasterXSize'] = str(totalXSize)
    rootNode.attrib['rasterYSize'] = str(totalYSize)

    node = ET.SubElement(rootNode, 'SRS')
    node.text = ds.GetProjection() # projection

    stringToReturn = ET.tostring(rootNode)
    logger.debug(stringToReturn)


    #if not os.path.isfile( vrt_name):
    writer = open( vrt_name, 'w')
    writer.write( stringToReturn )
    writer.close()

 
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #parser.add_argument('--filelist', nargs='*', type=argparse.FileType('r'))
    parser.add_argument('--filelist', nargs='*')
    parser.add_argument('--vrtfile')
    args = parser.parse_args()
    
    #filelist=["QB_1_ortho.tif","QB_1_ortho_NDWI.tif","QB_1_ortho_NDVI.tif"]
    #vrt_name = "testVRT3.vrt"
    create_vrt_from_filelist(args.vrtfile, args.filelist)

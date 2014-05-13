# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-05-13
        copyright            : (C) 2014 by CNES
        email                : alexia.mondot@c-s.fr
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
import datetime
import shutil

from working_layer import WorkingLayer
from manage_bands import manage_bands
import manage_QGIS
import terre_image_processing

from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QDir, QSettings

from osgeo import gdal

#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'Terre_Image_Utils' )
logger.setLevel(logging.DEBUG)

def fill_default_directory( ):
    """
    Creates working directory 
    Fills the output directory line edit if ui given
    """
    datetimeNow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    currentDirectory = os.path.join( os.getenv("HOME"), "TerreImage", datetimeNow )
    if not os.path.exists( currentDirectory ):
        os.makedirs( currentDirectory )
    return currentDirectory, datetimeNow



def working_layer(canvas):
    source = canvas.currentLayer().source()
    layer = WorkingLayer(source, canvas.currentLayer())
    
    
    #self.layer = self.canvas.currentLayer()
    if layer :
        #self.define_bands(self.layer)
        #manage_bands()
        #self.red, self.green, self.blue, self.pir, self.mir = manage_bands().get_values()
        red, green, blue, pir, mir = manage_bands().get_values()
        
        bands = { 'red':red, 'green':green, 'blue':blue, 'pir':pir, 'mir':mir }
        layer.set_bands(bands)
        
        
        print red, green, blue, pir, mir
        return layer
        
        
        
def get_workinglayer_on_opening(iface):
    settings = QSettings()
    lastFolder = settings.value("terre_image_lastFolder")
    
    if lastFolder:
        path = lastFolder
    else:
        path = QDir.currentPath()
        
        
    fileOpened = QFileDialog.getOpenFileName( None, "Select the QGIS project or a raster", path )
    
    settings.setValue("terre_image_lastFolder", os.path.dirname(fileOpened))
    settings.sync()
    
    if fileOpened:
        if fileOpened.endswith( ".qgs" ):
            #open new qgis project
            pass
        else :
            raster_layer = manage_QGIS.get_raster_layer(fileOpened, os.path.splitext(os.path.basename(fileOpened))[0])
            
            type_image = terre_image_processing.get_sensor_id(fileOpened)
            print "type_image", type_image
            layer = WorkingLayer( fileOpened, raster_layer )
            layer.set_type(type_image)
            #self.layer = self.canvas.currentLayer()
            if layer :
                #self.define_bands(self.layer)
                #manage_bands()
                #self.red, self.green, self.blue, self.pir, self.mir = manage_bands().get_values()
                red, green, blue, pir, mir = manage_bands(type_image).get_values()
                
                bands = { 'red':red, 'green':green, 'blue':blue, 'pir':pir, 'mir':mir }
                layer.set_bands(bands)
                
                print red, green, blue, pir, mir
                manage_QGIS.add_qgis_raser_layer(raster_layer, bands)
                return layer, bands
    
    
def computeStatistics( OneFeature, i, j=None, nodata=True ):
    """
    From the given feature, computes its statistics
    
    Keyword Arguments :
        OneFeature    --    raster layer to analyze
        i             --    only for debugging
    """
    
    logger.debug("one feature : " + OneFeature )
    
    #saving the feature only for testing
    outOne = OneFeature + str( i ) + ".tif" 
    shutil.copy( OneFeature, outOne )
    logger.debug( outOne )
    #/testing
    
    dataset = gdal.Open(str(OneFeature), gdal.GA_ReadOnly)
    # dataset  : GDALDataset
    if dataset is None:
        print "Error : Opening file ", OneFeature
    else :
        if j == None :
            band = dataset.GetRasterBand(1)
        else :
            band = dataset.GetRasterBand(j)
        if nodata :
            band.SetNoDataValue(0)
        stats = band.ComputeStatistics(False)
        
        logger.debug( "Feature " + str(i) + " : " )
        logger.debug( stats )
        return stats
        
    dataset = None
    return None    
    
    
    
        
        
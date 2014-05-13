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

from working_layer import WorkingLayer
from manage_bands import manage_bands
import manage_QGIS

from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QDir


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
    path = QDir.currentPath()
    fileOpened = QFileDialog.getOpenFileName( None, "Select the QGIS project or a raster", path )
    
    if fileOpened.endswith( ".qgs" ):
        #open new qgis project
        pass
    else :
        raster_layer = manage_QGIS.addRasterLayerToQGIS(fileOpened, os.path.splitext(os.path.basename(fileOpened))[0], iface)
        layer = WorkingLayer( fileOpened, raster_layer )
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
    
    
    
    
    
    
    
    
    
        
        
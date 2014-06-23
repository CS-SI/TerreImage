# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-05-12
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


#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'TerreImage_WorkingLayer' )
logger.setLevel(logging.DEBUG)


class WorkingLayer():
    def __init__(self, layer_file, qgis_layer, bands=None):
        
        self.source_file = layer_file
        self.qgis_layer = qgis_layer
        
        
        self.bands = bands
        self.set_bands(bands)
            
        self.type = None
        
    
    def __str__(self):
        message = "Working Layer : \n\t " + self.source_file + " " + str(self.bands)
        
        return message
    
        
    def set_bands(self, bands):
        if bands :
            self.bands = bands
            self.red    = bands['red']
            self.green  = bands['green']
            self.blue   = bands['blue']
            self.pir    = bands['pir']
            self.mir    = bands['mir']
            self.band_invert = dict((v,k) for k, v in self.bands.iteritems())
            logger.info( self.bands )
            logger.info( self.band_invert )
        
        
        
    def name(self):
        return self.qgis_layer.name()
        
        
    def get_qgis_layer(self):
        return self.qgis_layer
    
    def get_source(self):
        return self.source_file
    
    
    def get_band_number(self):
        return self.qgis_layer.bandCount()
        
        
    def set_type(self, type):
        self.type = type
        
    def has_natural_colors(self):
        return self.red not in [0,-1] and self.green not in [0,-1] and self.blue not in [0,-1]
        
        
        
        
        
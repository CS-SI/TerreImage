# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISEducation
                                 A QGIS plugin
 QGISEducation
                             -------------------
        begin                : 2014-05-12
        copyright            : (C) 2014 by CS SI
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



class WorkingLayer():
    def __init__(self, layer_file, qgis_layer, bands=None):
        
        self.source_file = layer_file
        self.qgis_layer = qgis_layer
        
        if bands :
            self.set_bands(bands)
        
        
        
    def set_bands(self, bands):
        self.red    = bands['red']
        self.green  = bands['green']
        self.blue   = bands['blue']
        self.pir    = bands['pir']
        self.mir    = bands['mir']
        
        
    def name(self):
        return self.qgis_layer.name()
        
        
    def get_qgis_layer(self):
        return self.qgis_layer
        
        
        
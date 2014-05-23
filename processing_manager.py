# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS_Edu
                                 A QGIS plugin
 Segmentation using OTB application
                              -------------------
        begin                : 2014-05-06
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

from PyQt4 import QtCore, QtGui
import terre_image_utils
from terre_image_task import TerreImageProcessing



class ProcessingManager():
    
    def __init__(self, iface ):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        self.working_directory, _ = terre_image_utils.fill_default_directory()
        self.layer = None
        self.processings = []
        
        self.layers_for_value_tool = [ ]
        
        
    def add_processing(self, processing):
        self.processings.append(processing)
        if isinstance(processing, TerreImageProcessing):
            self.layers_for_value_tool.append(processing.output_layer)
        print " adding", processing. processing_name
        print "self.layers_for_value_tool", self.layers_for_value_tool
        
    
    def set_current_layer(self):
        self.layer, bands  = terre_image_utils.get_workinglayer_on_opening( self.iface )
        self.layers_for_value_tool.append(self.layer ) #.get_qgis_layer())
        print "set_current_layer: layers_for_value_tool", self.layers_for_value_tool
        return self.layer, bands
        
        
    def __str__(self):
        sortie = "working_dir : " + self.working_directory + "\n"
        sortie += "image de travail : " + self.layer + "\n"
        
        return sortie
        

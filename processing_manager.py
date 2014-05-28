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
        
        
        self.layer = None
        self.working_directory = None #, _ = terre_image_utils.fill_default_directory()

        self.processings = []
        
        self.layers_for_value_tool = [ ]
        
        
    def add_processing(self, processing):
        self.processings.append(processing)
        if isinstance(processing, TerreImageProcessing):
            self.layers_for_value_tool.append(processing.output_layer)
        print " adding", processing. processing_name
        print "self.layers_for_value_tool", self.layers_for_value_tool
        
        
    def get_process_to_display(self):
        for x in self.processings:
            print x
            print x.output_layer
        
        
        temp = [x.output_layer for x in self.processings if isinstance(x, TerreImageProcessing) and x.output_layer is not None]
        print temp
        return temp
        
    
    def set_current_layer(self):
        self.layer, bands  = terre_image_utils.get_workinglayer_on_opening( self.iface )
        if self.layer:
            self.working_directory = os.path.join(os.path.dirname(self.layer.source_file), "working_directory")
            if not os.path.exists( self.working_directory ):
                os.makedirs( self.working_directory )
                
        self.layers_for_value_tool.append(self.layer ) #.get_qgis_layer())
        print "set_current_layer: layers_for_value_tool", self.layers_for_value_tool
        print "working directory"
        return self.layer, bands
        
        
    def __str__(self):
        sortie = "working_dir : " + self.working_directory + "\n"
        sortie += "image de travail : " + str(self.layer) + "\n"
        sortie += "processings : ["
        for pro in self.processings:
            sortie += str(pro) + "\n"
        sortie += "]"
        return sortie
    
    def restore_processing_manager(self, filename, bands, type):
        self.layer, bands  = terre_image_utils.restore_working_layer( filename, bands, type )
        self.layers_for_value_tool.append(self.layer )
        return self.layer, bands
        
        
        
        

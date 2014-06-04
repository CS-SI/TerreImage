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
from qgis.core import QgsMapLayerRegistry

from valuetool.valuewidget import ValueWidget
from DockableMirrorMap.dockableMirrorMapPlugin import DockableMirrorMapPlugin



class ProcessingManager():
    
    def __init__(self, iface ):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.layer = None
        self.working_directory = None #, _ = terre_image_utils.fill_default_directory()
        self.processings = []
        self.layers_for_value_tool = [ ]
        self.name_to_processing = {}
        
        self.value_tool = ValueWidget( self.iface ) #, self )
        #creating a dock widget
        # create the dockwidget with the correct parent and add the valuewidget
        self.valuedockwidget = QtGui.QDockWidget("Values", self.iface.mainWindow() )
        self.valuedockwidget.setObjectName("Values")
        self.valuedockwidget.setWidget(self.value_tool)
        self.iface.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.valuedockwidget)
        self.valuedockwidget.hide()
        print self.value_tool
        
        self.mirror_map_tool = DockableMirrorMapPlugin(self.iface)
        self.mirror_map_tool.initGui()
        QtCore.QObject.connect(self.mirror_map_tool, QtCore.SIGNAL( "mirrorClosed(PyQt_PyObject)" ), self.view_closed)
        
        #self.angle_tool = SpectralAngle(self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool)
        
        
    def add_processing(self, processing):
        self.processings.append(processing)
        if isinstance(processing, TerreImageProcessing):
            self.layers_for_value_tool.append(processing.output_working_layer.qgis_layer)
        print " adding", processing.processing_name
        self.name_to_processing[processing.processing_name] = processing
        print "self.layers_for_value_tool", self.layers_for_value_tool
        
        
    def get_process_to_display(self):
        for x in self.processings:
            print x
            print x.output_working_layer.qgis_layer
        
        
        temp = [x.output_working_layer.qgis_layer for x in self.processings if isinstance(x, TerreImageProcessing) and x.output_working_layer.qgis_layer is not None]
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
        
        
    def display_values(self):
        
        self.valuedockwidget.show()
        self.value_tool.changeActive( QtCore.Qt.Checked )
        self.value_tool.cbxActive.setCheckState( QtCore.Qt.Checked )
        self.value_tool.set_layers([self.layer] + self.get_process_to_display())
        
        
    def view_closed(self, name_of_the_closed_view):
        print name_of_the_closed_view,  " has been closed"
        process = self.name_to_processing[name_of_the_closed_view]
        QgsMapLayerRegistry.instance().removeMapLayer( process.output_working_layer.qgis_layer.id())
        self.remove_process(process)
        
        
    def remove_process(self, process):
        if process in self.processings :
            self.processings.remove(process)
            if isinstance(process, TerreImageProcessing):
                self.layers_for_value_tool.remove(process.output_working_layer.qgis_layer)
        self.name_to_processing[process.processing_name] = ""
        
        
    def removing_layer(self, layer_id):
        process = [ p for p in self.processings if p.output_working_layer.qgis_layer.id() == layer_id ]
        print "process", process
        if process :
            process[0].mirror.close()
            self.remove_process(process[0])
        
        
    def disconnect(self):
        #disconnect value tool
        self.iface.mainWindow().statusBar().clearMessage()
        try :
            self.value_tool.changeActive( QtCore.Qt.Unchecked )
            self.value_tool.set_layers([])
            self.value_tool.close()
            self.value_tool.disconnect()
            self.value_tool = None
        except AttributeError:
            pass    
        
                
        # disconnect dockable mirror map
        self.mirror_map_tool.unload()
        
        # remove the dockwidget from iface
        self.iface.removeDockWidget(self.valuedockwidget)
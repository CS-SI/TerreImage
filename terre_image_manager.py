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
from processing_manager import ProcessingManager

from valuetool.valuewidget import ValueWidget
from DockableMirrorMap.dockableMirrorMapPlugin import DockableMirrorMapPlugin
from ClassificationSupervisee.supervisedclassificationdialog import SupervisedClassificationDialog


#import loggin for debug messages
import logging
logging.basicConfig()
# create logger
logger = logging.getLogger( 'TerreImage_TerreImageManager' )
logger.setLevel(logging.INFO)

class TerreImageManager():
    
    def __init__(self, iface ):
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.layer = None
        self.working_directory = None #, _ = terre_image_utils.fill_default_directory()
        self.processings = []
        
        self.value_tool = ValueWidget( self.iface ) #, self )
        #creating a dock widget
        # create the dockwidget with the correct parent and add the valuewidget
        self.valuedockwidget = QtGui.QDockWidget("Valeurs spectrales", self.iface.mainWindow() )
        self.valuedockwidget.setObjectName("Valeurs spectrales")
        self.valuedockwidget.setWidget(self.value_tool)
        self.iface.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.valuedockwidget)
        self.valuedockwidget.hide()
        logger.info( self.value_tool )
        
        self.mirror_map_tool = DockableMirrorMapPlugin(self.iface)
        self.mirror_map_tool.initGui()
        QtCore.QObject.connect(self.mirror_map_tool, QtCore.SIGNAL( "mirrorClosed(PyQt_PyObject)" ), self.view_closed)
        
        #self.angle_tool = SpectralAngle(self.iface, self.qgis_education_manager.working_directory, self.layer, self.mirror_map_tool)
        
        self.classif_tool = SupervisedClassificationDialog(self.iface)
        
        
    
    def set_current_layer(self):
        self.layer, bands  = terre_image_utils.get_workinglayer_on_opening( self.iface )
        if self.layer:
            self.working_directory = os.path.join(os.path.dirname(self.layer.source_file), "working_directory")
            terre_image_utils.update_subdirectories(self.working_directory)
            if not os.path.exists( self.working_directory ):
                os.makedirs( self.working_directory )
            ProcessingManager().working_layer = self.layer
            self.classif_tool.set_layers(ProcessingManager().get_qgis_working_layers(), self.layer.get_qgis_layer(), self.layer.band_invert)
            self.classif_tool.set_directory(self.working_directory)
            self.classif_tool.setupUi()
        #self.layers_for_value_tool.append(self.layer ) #.get_qgis_layer())
        logger.debug( "working directory" )
        
        return self.layer, bands
        
        
    def __str__(self):
        sortie = "working_dir : " + self.working_directory + "\n"
        sortie += "image de travail : " + str(self.layer) + "\n"
        sortie += "processings : ["
        for pro in self.processings:
            sortie += str(pro) + "\n"
        sortie += "]"
        
        return sortie
    
    def restore_processing_manager(self, filename, bands, type, working_dir):
        self.layer, bands  = terre_image_utils.restore_working_layer( filename, bands, type )
        ProcessingManager().working_layer = self.layer
        #self.layers_for_value_tool.append(self.layer )
        self.working_directory = working_dir
        return self.layer, bands
        
        
    def display_values(self):
        
        self.valuedockwidget.show()
        self.value_tool.changeActive( QtCore.Qt.Checked )
        self.value_tool.cbxActive.setCheckState( QtCore.Qt.Checked )
        self.value_tool.set_layers(ProcessingManager().get_working_layers())
        
        
    def view_closed(self, name_of_the_closed_view):
        #print str(name_of_the_closed_view) + " has been closed"
        logger.debug( str(name_of_the_closed_view) + " has been closed")
        process = ProcessingManager().processing_from_name(name_of_the_closed_view)
        #print process
        if process :
            try:
                QgsMapLayerRegistry.instance().removeMapLayer( process[0].output_working_layer.qgis_layer.id())
                ProcessingManager().remove_process(process[0])
                ProcessingManager().remove_display(process[0])
            except KeyError:
                pass
        
        
    def removing_layer(self, layer_id):
        ProcessingManager().remove_process_from_layer_id(layer_id)
    
        
        
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